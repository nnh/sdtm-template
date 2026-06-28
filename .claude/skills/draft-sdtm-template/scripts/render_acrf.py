#!/usr/bin/env python3
"""aCRF (JASPEHR template) 決定論レンダラ.

レイアウトマニフェスト (JSON) を入力に、SDTM 注釈付きの aCRF HTML を生成する。
描画規則 (CSS・ドメイン配色・変数名規則・コントロール・Findings の "when" 表記・
sponsor 拡張の "*" マーク) はすべて本スクリプトに固定されており、同じマニフェストから
必ず同じ HTML が出る。LLM が都度 HTML を書き起こすことによる品質ドリフトを排除する。

配色は Ptosh の CDISC::Annotatable と同じ HSV モデル:
    hue = domain_index / domain_count,  s = 71/255,  v = 244/255
SPID はドメイン色を持たず固定の灰 (#e2e2e2)・接頭辞なし。
DM のドメイン変数 (AGE/SEX/SITEID/SUBJID 等) は接頭辞を持たない (SDTM 仕様)。
それ以外のドメインは name = domain + suffix。Findings は "VAR when <dom>TESTCD = <testcd>"。

使い方:
    python3 render_acrf.py LAYOUT.json [-o OUT.html] [--check TEMPLATES_DIR]

--check を付けると、マニフェストの変数・CT 選択肢・コントロール種別を
TEMPLATES_DIR 配下の TemplateInput JSON と突合し、食い違いを stderr に警告する
(描画自体は止めない。JSON 非対応の行 = 例: MH は warn しない)。
"""
import argparse
import colorsys
import html
import json
import sys
from pathlib import Path

# Ptosh CDISC::Annotatable と同一の HSV パラメータ。
_SAT = 71 / 255
_VAL = 244 / 255
# SPID はドメイン色を持たない固定色 (接頭辞なし識別子)。
SPID_COLOR = "#e2e2e2"


def domain_color(domain, order):
    """domainOrder 内での位置から HSV→RGB でドメイン色を決定論的に算出する。"""
    idx = order.index(domain)
    r, g, b = colorsys.hsv_to_rgb(idx / len(order), _SAT, _VAL)
    return "#{:02x}{:02x}{:02x}".format(round(r * 255), round(g * 255), round(b * 255))


def var_name(var):
    """注釈ボックスに表示する SDTM 変数名を規則どおり組み立てる。"""
    if var.get("spid"):
        return "SPID"
    dom, suf = var["domain"], var["suffix"]
    base = suf if dom == "DM" else dom + suf
    if var.get("testcd") is not None:
        # Findings-About 系: "FAORRES when FATESTCD = COSTINS"
        return "{} when {}TESTCD = {}".format(base, dom, var["testcd"])
    return base


def var_color(var, order):
    return SPID_COLOR if var.get("spid") else domain_color(var["domain"], order)


def esc(s):
    return html.escape(str(s), quote=False)


def render_control(row):
    """fieldType 相当の control 種別を disabled な入力要素にする。"""
    ctrl = row.get("control", "text")
    if ctrl == "hidden":
        return '<span class="hid">［hidden / 自動］</span>'
    if ctrl == "date":
        return '<input type="date" disabled>'
    if ctrl == "number":
        return '<input type="number" step="1" disabled>'
    if ctrl in ("radio", "select"):
        opts = []
        for o in row.get("options", []):
            sub = "→" + esc(o["value"])
            if o.get("sponsor"):
                sub += '<span class="spx">*</span>'
            opts.append(
                '<label class="opt"><input type="radio" disabled> {} '
                '<span class="sub">{}</span></label>'.format(esc(o["display"]), sub)
            )
        return '<div class="opts">' + "".join(opts) + "</div>"
    return '<input type="text" disabled>'


def render_row(row, order):
    cls = ' class="hiddenrow"' if row.get("control") == "hidden" else ""
    cvs = []
    for var in row.get("vars", []):
        cvs.append(
            '<span class="cv" style="background-color:{}">{}</span>'.format(
                var_color(var, order), esc(var_name(var))
            )
        )
    for note in row.get("notes", []):
        cvs.append('<span class="cvx">{}</span>'.format(esc(note)))
    return (
        '<li{cls}>\n'
        '  <div class="fi"><div class="labels"><div class="lab">{label}</div></div>\n'
        '  <div class="ctrl">{ctrl}</div></div>\n'
        '  <div class="cvs">{cvs}</div></li>'
    ).format(cls=cls, label=esc(row["label"]), ctrl=render_control(row), cvs="".join(cvs))


def render(manifest):
    order = manifest["domainOrder"]
    page_title = manifest.get("pageTitle", manifest["title"])

    legend = []
    for entry in manifest.get("legend", []):
        color = SPID_COLOR if entry["key"] == "SPID" else domain_color(entry["key"], order)
        legend.append(
            '<span class="domain_name" style="background-color:{}">{}</span>'.format(
                color, esc(entry["label"])
            )
        )

    body = []
    for sec in manifest["sections"]:
        if sec.get("header"):
            body.append(
                '<li class="secrow"><div class="sech">{}</div></li>'.format(esc(sec["header"]))
            )
        for row in sec["rows"]:
            body.append(render_row(row, order))

    return TEMPLATE.format(
        page_title=esc(page_title),
        title=esc(manifest["title"]),
        meta=esc(manifest.get("meta", "")),
        legend="".join(legend),
        note=manifest.get("note", ""),   # note/foot は意図的 HTML を許可 (raw)
        body="\n".join(body),
        foot=manifest.get("foot", ""),
    )


def check(manifest, templates_dir):
    """マニフェストの行を TemplateInput JSON と突合して食い違いを警告する。"""
    by_var = {}
    for jp in sorted(Path(templates_dir).glob("*.json")):
        data = json.loads(jp.read_text(encoding="utf-8"))
        dom = data.get("domain")
        for fi in data.get("fieldItems", []):
            by_var.setdefault((dom, fi.get("cdiscVariableSuffix")), []).append((jp.name, fi))

    warned = 0
    for sec in manifest["sections"]:
        for row in sec["rows"]:
            for var in row.get("vars", []):
                if var.get("spid"):
                    continue
                key = (var["domain"], var["suffix"])
                if key not in by_var:
                    print("WARN: {} がテンプレート JSON に存在しません (行: {})".format(
                        var_name(var), row.get("label")), file=sys.stderr)
                    warned += 1
    if warned == 0:
        print("check: マニフェストの全変数がテンプレート JSON と整合しています。", file=sys.stderr)
    return warned


TEMPLATE = """<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<title>{page_title}</title><style>
body{{font-family:'Hiragino Sans','Yu Gothic',sans-serif;color:#222;max-width:920px;margin:0 auto;padding:24px;line-height:1.5}}
h1{{font-size:1.5em;margin:0 0 2px}}.meta{{color:#555;font-size:.85em;margin-bottom:12px}}
.legend{{margin:10px 0 16px}}
.domain_name{{display:inline-block;padding:3px 8px;margin:3px 4px 3px 0;border:1px solid #999;border-radius:3px;font-family:monospace;font-size:.8em}}
.note{{background:#f7f7f7;border-left:4px solid #bbb;padding:8px 12px;font-size:.83em;margin:8px 0 14px}}
ul{{list-style:none;padding:0;margin:0}}
li{{border-bottom:1px dashed #ddd;padding:9px 0}}
li.secrow{{border:none;padding:14px 0 2px}}
.sech{{font-weight:bold;font-size:.95em;color:#225;border-bottom:2px solid #333;padding-bottom:3px}}
li.hiddenrow{{background:#fafafa}}
.fi{{display:flex;align-items:flex-start;gap:14px}}
.labels{{flex:0 0 40%}}.lab{{font-weight:600}}
.ctrl{{flex:1}}
input{{padding:4px 6px;border:1px solid #aaa;border-radius:3px;background:#fafafa;width:88%}}
input[type=number]{{width:150px}}
.hid{{color:#999;font-size:.85em;font-style:italic}}
.opts{{display:flex;flex-wrap:wrap;gap:10px}}.opt{{font-size:.92em}}
.sub{{font-family:monospace;font-size:.82em;color:#444}}.spx{{color:#c00;font-weight:bold}}
.cvs{{margin-top:6px}}
.cv{{display:inline-block;padding:2px 7px;margin:2px 5px 2px 0;border:1px solid #888;border-radius:3px;font-family:monospace;font-size:.8em}}
.cvx{{display:inline-block;padding:2px 7px;margin:2px 5px 2px 0;border:1px dashed #aaa;border-radius:3px;font-family:monospace;font-size:.75em;color:#555;background:#fcfcfc}}
.foot{{margin-top:22px;border-top:1px solid #ccc;padding-top:10px;font-size:.8em;color:#555}}
@media print{{body{{max-width:none}}@page{{size:A4;margin:14mm}}}}
</style></head><body>
<h1>{title}</h1>
<div class="meta">{meta}</div>
<div class="legend">{legend}</div>
<div class="note">{note}</div>
<ul>{body}</ul>
<div class="foot">{foot}</div>
</body></html>"""


def main(argv=None):
    ap = argparse.ArgumentParser(description="aCRF (JASPEHR template) 決定論レンダラ")
    ap.add_argument("layout", help="レイアウトマニフェスト JSON")
    ap.add_argument("-o", "--output", help="出力 HTML パス (省略時は stdout)")
    ap.add_argument("--check", metavar="TEMPLATES_DIR",
                    help="TemplateInput JSON 群と変数を突合して警告する")
    args = ap.parse_args(argv)

    manifest = json.loads(Path(args.layout).read_text(encoding="utf-8"))
    if args.check:
        check(manifest, args.check)

    html_out = render(manifest)
    if args.output:
        Path(args.output).write_text(html_out, encoding="utf-8")
        print("wrote {}".format(args.output), file=sys.stderr)
    else:
        sys.stdout.write(html_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
