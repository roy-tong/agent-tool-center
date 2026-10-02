#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""report-html —— 把一份或多份 Markdown 报告合并成单个自包含 HTML 交付物。

左侧文档树（分组 + 全文搜索）+ 内容面板，样式与脚本全部内嵌，无外部依赖、
无第三方 Python 依赖，CJK 安全，生成后可直接发人。

来源谱系：从 projects/高尔夫智能设备调研/scripts/build_html.py 泛化——
- md_to_html / inline 两个函数原样保留（battle-tested 的最小 md 转换器）
- 文档清单从硬编码的 DOCS 改为 CLI（--input 文件/目录）或清单文件（--manifest）
- 按 `# ` 一级标题把单份 md 切成多章树节点（吸收自 build_final_html.py 的 split_chapters）
- :root 主题变量可覆盖（--theme 或 manifest 的 theme 字段）

三种用法：
  # 1) 单份 md 按 # 切章（终稿模式）
  python3 build_report_html.py -i 报告.md --split -o out.html --title "XX 项目 · 终稿"
  # 2) 多份 md / 目录（目录递归收集 *.md，一级子目录名成为分组）
  python3 build_report_html.py -i 05-整合文档 -i 06-report/定价研究.md -o out.html
  # 3) 清单模式（文件→树节点标题映射、分组、顺序、主题，见 README.md）
  python3 build_report_html.py -m manifest.json
"""
from __future__ import annotations

import argparse
import datetime
import html
import json
import pathlib
import re
import sys

# --------------------------------------------------------------------------
# 主题：默认 = 高尔夫总览的绿色版式；新增 accent-soft/code-bg/mark-bg 三个变量，
# 把原 CSS 里的硬编码颜色（#eef5f1 / #f0f0ec / #ffe9a8）提为变量，供 --theme 覆盖。
# --------------------------------------------------------------------------
DEFAULT_THEME = {
    "bg": "#f7f7f5",
    "panel": "#ffffff",
    "ink": "#1a1a1a",
    "sub": "#6b6b6b",
    "line": "#e4e4e0",
    "accent": "#0f6b4f",
    "accent-ink": "#0b4a37",
    "accent-soft": "#eef5f1",
    "code-bg": "#f0f0ec",
    "mark-bg": "#ffe9a8",
}


# --------------------------------------------------------------------------
# md 转换器 —— 高尔夫 build_html.py 原样保留，勿改动解析行为
# （headers/tables/lists/bold/links/hr/blockquote/code，CJK 安全）
# --------------------------------------------------------------------------
def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\w)\*([^*\n]+)\*(?!\w)", r"<em>\1</em>", s)
    return s


def md_to_html(md: str) -> str:
    lines = md.splitlines()
    out, i, in_list = [], 0, False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            close_list(); i += 1; continue
        if stripped.startswith("```"):
            close_list(); out.append("<pre><code>")
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                out.append(html.escape(lines[i])); i += 1
            out.append("</code></pre>"); i += 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            close_list()
            lvl = min(len(m.group(1)) + 1, 6)
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1; continue
        if re.match(r"^(-{3,}|\*{3,})$", stripped):
            close_list(); out.append("<hr>"); i += 1; continue
        if stripped.startswith(">"):
            close_list(); out.append(f"<blockquote>{inline(stripped.lstrip('> ').rstrip())}</blockquote>")
            i += 1; continue
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|?$", lines[i + 1].strip()):
            close_list()
            header = [c.strip() for c in stripped.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            t = "<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in header) + "</tr></thead><tbody>"
            for r in rows:
                t += "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
            t += "</tbody></table>"
            out.append(t); continue
        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if m:
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{inline(m.group(1))}</li>"); i += 1; continue
        m = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
        if m:
            if not in_list:
                out.append("<ul class='num'>"); in_list = True
            out.append(f"<li>{inline(m.group(2))}</li>"); i += 1; continue
        close_list()
        out.append(f"<p>{inline(stripped)}</p>"); i += 1
    close_list()
    return "\n".join(out)


# --------------------------------------------------------------------------
# 切章 —— 吸收自高尔夫 build_final_html.py（唯一改动：全空白的前言不再生成空"封面"）
# --------------------------------------------------------------------------
def split_chapters(md: str, cover_label: str = "封面"):
    """按 `# ` 一级标题切分；首个标题之前的前言成为第一个树节点（封面）。"""
    lines = md.splitlines()
    chunks, cur, title = [], [], None
    for line in lines:
        m = re.match(r"^# (.+)$", line.strip())
        if m:
            if cur and any(l.strip() for l in cur):
                chunks.append((title, "\n".join(cur)))
            title, cur = m.group(1), []
        else:
            cur.append(line)
    if cur and any(l.strip() for l in cur):
        chunks.append((title, "\n".join(cur)))
    return [(t if t else cover_label, body) for t, body in chunks]


def first_h1(md: str) -> str | None:
    for line in md.splitlines():
        m = re.match(r"^# (.+)$", line.strip())
        if m:
            return m.group(1).strip()
    return None


# --------------------------------------------------------------------------
# 输入收集：--input（文件/目录，可重复）或 --manifest（清单 JSON）
# 统一产出 items：("group", 标题) 或 ("doc", 标题, 路径或None, md文本或None)
# --------------------------------------------------------------------------
def iter_dir_md(root: pathlib.Path):
    """目录内递归收集 *.md（跳过隐藏文件/目录），按相对路径排序。"""
    out = []
    for p in root.rglob("*.md"):
        if p.suffix.lower() != ".md":
            continue
        rel = p.relative_to(root)
        if any(part.startswith(".") for part in rel.parts):
            continue
        out.append(p)
    out.sort(key=lambda p: str(p.relative_to(root)))
    return out


def read_doc(path: pathlib.Path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # 少数旧文件可能是 GBK/GB18030
        return path.read_text(encoding="gb18030")


def collect_inputs(args) -> list:
    base = pathlib.Path(args.root).expanduser() if args.root else pathlib.Path.cwd()
    items, seen = [], set()

    def add_file(p: pathlib.Path, label=None, split=None):
        if p in seen:
            return
        seen.add(p)
        md = read_doc(p)
        do_split = args.split if split is None else split
        if do_split:
            for t, body in split_chapters(md, args.cover_label):
                items.append(("doc", t, p.name, body))
        else:
            items.append(("doc", label or first_h1(md) or p.stem, p.name, md))

    for raw in args.input:
        p = pathlib.Path(raw).expanduser()
        if not p.is_absolute():
            p = base / p
        if not p.exists():
            sys.exit(f"[report-html] 输入不存在：{p}")
        if p.is_dir():
            cur_group = None
            for f in iter_dir_md(p):
                rel = f.relative_to(p)
                if len(rel.parts) > 1:
                    g = rel.parts[0]
                    if g != cur_group:
                        items.append(("group", g))
                        cur_group = g
                else:
                    cur_group = None
                add_file(f)
        else:
            add_file(p)
    return items


def collect_manifest(args, mf: pathlib.Path, mf_data: dict) -> tuple:
    """清单模式。file 相对路径基于清单所在目录（--root 可覆盖）。"""
    base = pathlib.Path(args.root).expanduser() if args.root else mf.parent
    default_split = bool(args.split or mf_data.get("split", False))
    entries = mf_data.get("docs")
    if not isinstance(entries, list) or not entries:
        sys.exit(f"[report-html] 清单缺少 docs 数组：{mf}")

    items = []
    for idx, e in enumerate(entries):
        if not isinstance(e, dict):
            sys.exit(f"[report-html] 清单第 {idx} 项必须是对象：{e!r}")
        if "group" in e:
            items.append(("group", str(e["group"])))
            continue
        if "file" not in e:
            sys.exit(f"[report-html] 清单第 {idx} 项缺少 file 或 group 字段：{e!r}")
        rel = str(e["file"])
        p = pathlib.Path(rel).expanduser()
        if not p.is_absolute():
            p = base / p
        label = str(e["title"]) if e.get("title") else None
        split = bool(e["split"]) if "split" in e else None
        if p.exists():
            md = read_doc(p)
            do_split = default_split if split is None else split
            if do_split:
                for t, body in split_chapters(md, args.cover_label):
                    items.append(("doc", t, p.name, body))
            else:
                items.append(("doc", label or first_h1(md) or p.stem, p.name, md))
        else:
            # 与高尔夫版一致：缺失文件不中断，渲染占位并告警
            print(f"[report-html] 警告：缺失文件 {rel}", file=sys.stderr)
            items.append(("doc", label or p.stem, rel, None))
    return items


# --------------------------------------------------------------------------
# 主题
# --------------------------------------------------------------------------
def parse_theme_pairs(pairs) -> dict:
    out = {}
    for pair in pairs:
        for kv in pair.split(","):
            kv = kv.strip()
            if not kv:
                continue
            if "=" not in kv:
                sys.exit(f'[report-html] --theme 格式应为 变量=颜色，收到："{kv}"')
            k, v = kv.split("=", 1)
            k, v = k.strip(), v.strip()
            if k not in DEFAULT_THEME:
                sys.exit(f"[report-html] 未知主题变量 {k}；可用：{', '.join(DEFAULT_THEME)}")
            if not v or re.search(r"[;{}<>]", v):
                sys.exit(f'[report-html] 非法颜色值 "{v}"（变量 {k}）')
            out[k] = v
    return out


def theme_css(overrides: dict) -> str:
    merged = {**DEFAULT_THEME, **overrides}
    return ";" + ";".join(f"--{k}:{v}" for k, v in merged.items()) + ";"


# --------------------------------------------------------------------------
# 页面模板 —— 高尔夫 build_html.py 的模板，占位符泛化
# --------------------------------------------------------------------------
PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__HTML_TITLE__</title>
<style>
:root{__THEME__}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans GB","Noto Sans CJK SC","Yu Gothic UI",MalgunGothic,sans-serif;background:var(--bg);color:var(--ink);line-height:1.75}
.layout{display:flex;min-height:100vh}
aside{width:280px;flex:none;background:var(--panel);border-right:1px solid var(--line);padding:24px 0;position:sticky;top:0;height:100vh;overflow:auto}
.brand{padding:0 20px 16px;border-bottom:1px solid var(--line);margin-bottom:12px}
.brand h1{font-size:16px;margin:0 0 4px;color:var(--accent-ink)}
.brand p{margin:0;font-size:12px;color:var(--sub)}
.search{padding:8px 20px 10px;border-bottom:1px solid var(--line)}
.search input{width:100%;padding:6px 10px;border:1px solid var(--line);border-radius:6px;font-size:12.5px;background:#fafaf8}
.search input:focus{outline:none;border-color:var(--accent)}
.qinfo{font-size:11px;color:var(--sub);padding:4px 2px 0;min-height:14px}
.tree-link.dim{display:none}
.tree-group.dim{display:none}
mark{background:var(--mark-bg);padding:0 1px}
.tree-group{padding:14px 20px 6px;font-size:11px;letter-spacing:.12em;color:var(--sub);text-transform:uppercase}
.tree-link{display:block;padding:7px 20px 7px 26px;color:var(--ink);text-decoration:none;font-size:13.5px;border-left:3px solid transparent}
.tree-link:hover{background:var(--code-bg)}
.tree-link.active{border-left-color:var(--accent);color:var(--accent-ink);font-weight:600;background:var(--accent-soft)}
main{flex:1;padding:48px 56px;max-width:980px}
.doc{display:none;animation:fade .25s ease}
.doc.show{display:block}
@keyframes fade{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
h1,h2,h3,h4{line-height:1.35}
h2{border-bottom:1px solid var(--line);padding-bottom:8px;margin-top:44px}
h3{margin-top:30px}
table{border-collapse:collapse;width:100%;margin:16px 0;font-size:13.5px;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
th{background:var(--code-bg);font-weight:600}
blockquote{margin:12px 0;padding:8px 16px;border-left:3px solid var(--accent);background:var(--accent-soft);color:#333}
code{background:var(--code-bg);padding:1px 5px;border-radius:4px;font-size:.9em}
pre code{display:block;padding:12px;overflow-x:auto}
hr{border:none;border-top:1px solid var(--line);margin:32px 0}
a{color:var(--accent-ink)}
ul.num{list-style:decimal;padding-left:24px}
ul{padding-left:24px}
@media(max-width:900px){aside{display:none}main{padding:24px}.doc{display:block}}
</style>
</head>
<body>
<div class="layout">
<aside>
  <div class="brand"><h1>__TITLE__</h1><p>__SUBTITLE__</p></div>
  <div class="search"><input id="q" type="search" placeholder="搜索文档标题或全文…" oninput="filterDocs(this.value)"><div id="qinfo" class="qinfo"></div></div>
  __TREE__
</aside>
<main>
__SECTIONS__
</main>
</div>
<script>
function show(i){document.querySelectorAll('.doc').forEach(function(e){e.classList.remove('show')});
document.getElementById('doc'+i).classList.add('show');
document.querySelectorAll('.tree-link').forEach(function(e){e.classList.remove('active')});
document.querySelector('.tree-link[href="#doc'+i+'"]').classList.add('active');
window.scrollTo(0,0);}
function filterDocs(q){
q=q.trim().toLowerCase();
var links=document.querySelectorAll('.tree-link'),groups=document.querySelectorAll('.tree-group'),hit=0;
if(!q){links.forEach(function(e){e.classList.remove('dim')});groups.forEach(function(e){e.classList.remove('dim')});
document.getElementById('qinfo').textContent='';return;}
var firstHit=null;
links.forEach(function(e){e.classList.remove('dim');
var idx=e.getAttribute('href').slice(1);
var sec=document.getElementById(idx);
var inTitle=e.textContent.toLowerCase().indexOf(q)>-1;
var inBody=sec&&sec.textContent.toLowerCase().indexOf(q)>-1;
if(inTitle||inBody){hit++;if(!firstHit)firstHit=e;}else{e.classList.add('dim');}});
groups.forEach(function(g){g.classList.remove('dim');
var nb=false,s=g.nextElementSibling;
while(s&&!s.classList.contains('tree-group')){if(s.classList.contains('tree-link')&&!s.classList.contains('dim')){nb=true;break;}s=s.nextElementSibling;}
if(!nb)g.classList.add('dim');});
document.getElementById('qinfo').textContent=hit?('命中 '+hit+' 篇文档'):'无命中';
if(hit===1&&firstHit){var i=parseInt(firstHit.getAttribute('href').slice(3));if(!document.getElementById('doc'+i).classList.contains('show'))show(i);}
}
show(0);
</script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------
def build(items, title: str, subtitle: str, theme: dict):
    sections, tree_items = [], []
    doc_idx = 0
    for it in items:
        if it[0] == "group":
            tree_items.append(f'<div class="tree-group">{html.escape(it[1])}</div>')
            continue
        _, label, src, md = it
        if md is None:
            content = f"<p>缺失文件：{html.escape(str(src))}</p>"
        else:
            content = md_to_html(md)
        sections.append(f'<section class="doc" id="doc{doc_idx}">{content}</section>')
        tree_items.append(
            f'<a class="tree-link" href="#doc{doc_idx}" onclick="show({doc_idx});return false;">{html.escape(label)}</a>'
        )
        doc_idx += 1
    if doc_idx == 0:
        sys.exit("[report-html] 没有收集到任何 md 文档")

    if not any(it[0] == "group" for it in items):
        tree_items.insert(0, '<div class="tree-group">文档</div>')

    today = datetime.date.today().isoformat()
    sub_lines = []
    if subtitle:
        sub_lines.append(html.escape(subtitle).replace("\n", "<br>"))
    sub_lines.append(f"{today} · {doc_idx} 篇文档")

    page = PAGE
    page = page.replace("__HTML_TITLE__", html.escape(f"{title} · {doc_idx} 篇文档"))
    page = page.replace("__TITLE__", html.escape(title))
    page = page.replace("__SUBTITLE__", "<br>".join(sub_lines))
    page = page.replace("__THEME__", theme_css(theme))
    page = page.replace("__TREE__", "\n".join(tree_items))
    page = page.replace("__SECTIONS__", "\n".join(sections))
    return page, doc_idx


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="report-html",
        description="把一份或多份 Markdown 报告合并成单个自包含 HTML（左侧文档树 + 全文搜索）。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例：
  %(prog)s -i 报告.md --split -o out.html --title "XX 项目 · 终稿"
  %(prog)s -i 05-整合文档 -i 06-report/定价研究.md -o out.html --title "XX 调研"
  %(prog)s -m manifest.json
  %(prog)s -i 报告.md -o out.html --theme accent=#0f5ea8,accent-ink=#0a3f73,bg=#f7f8fa
""",
    )
    p.add_argument("-i", "--input", action="append", metavar="PATH",
                   help="md 文件或目录，可重复；目录递归收集 *.md，一级子目录名成为分组")
    p.add_argument("-m", "--manifest", metavar="FILE",
                   help="清单 JSON（docs 数组：group 分组 / file+title+split 文档；可含 title/subtitle/output/theme）")
    p.add_argument("-o", "--output", metavar="FILE", help="输出 HTML 路径（默认取清单里的 output）")
    p.add_argument("--title", help="页面主标题（默认：清单 title 或输出文件名去后缀）")
    p.add_argument("--subtitle", help="侧栏品牌区副标题（可含 \\n 换行；末尾自动附构建日期与文档数）")
    p.add_argument("--split", action="store_true",
                   help="把每份 md 按 # 一级标题切成多个树节点（章模式）；清单可按文档覆盖")
    p.add_argument("--theme", action="append", default=[], metavar="K=V",
                   help="覆盖 :root 主题变量，如 --theme accent=#0f5ea8 或 --theme accent=#0f5ea8,bg=#f7f8fa（可重复）")
    p.add_argument("--root", metavar="DIR", help="相对路径的基准目录（--input 默认当前目录；清单 file 默认清单所在目录）")
    p.add_argument("--cover-label", default="封面", help="--split 时首标题之前前言的节点名，默认：封面")
    args = p.parse_args(argv)

    if not args.input and not args.manifest:
        p.error("需要 --input（文件/目录）或 --manifest（清单）之一")
    if args.input and args.manifest:
        p.error("--input 与 --manifest 二选一，不要同时使用")
    return args


def main(argv=None) -> None:
    args = parse_args(argv)

    mf_data = {}
    mf = None
    if args.manifest:
        mf = pathlib.Path(args.manifest).expanduser()
        if not mf.is_absolute():
            mf = pathlib.Path.cwd() / mf
        if not mf.exists():
            sys.exit(f"[report-html] 清单不存在：{mf}")
        try:
            mf_data = json.loads(mf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            sys.exit(f"[report-html] 清单不是合法 JSON：{mf}\n  {e}")
        if isinstance(mf_data, list):  # 允许裸数组：只有 docs
            mf_data = {"docs": mf_data}
        if not isinstance(mf_data, dict):
            sys.exit(f"[report-html] 清单顶层应为对象或数组：{mf}")
        items = collect_manifest(args, mf, mf_data)
    else:
        items = collect_inputs(args)

    # 输出路径：--output > 清单 output > 报错
    out = args.output or mf_data.get("output")
    if not out:
        sys.exit("[report-html] 缺少输出路径：用 --output，或在清单里写 output")
    out_p = pathlib.Path(out).expanduser()
    if not out_p.is_absolute():
        out_p = (mf.parent if mf is not None and not args.output else pathlib.Path.cwd()) / out_p

    title = args.title or mf_data.get("title") or out_p.stem
    subtitle = args.subtitle if args.subtitle is not None else str(mf_data.get("subtitle") or "")

    theme = {}
    if isinstance(mf_data.get("theme"), dict):
        for k, v in mf_data["theme"].items():
            if k not in DEFAULT_THEME:
                sys.exit(f"[report-html] 清单 theme 里未知变量 {k}；可用：{', '.join(DEFAULT_THEME)}")
            theme[str(k)] = str(v)
    theme.update(parse_theme_pairs(args.theme))  # CLI 优先

    page, n_docs = build(items, title, subtitle, theme)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(page, encoding="utf-8")
    print(f"written {out_p} {len(page)} chars, {n_docs} docs")
    for it in items:
        if it[0] == "group":
            print(f"  [group] {it[1]}")
        else:
            src = "(缺失)" if it[3] is None else it[2]
            print(f"  doc    {it[1]}  <- {src}")


if __name__ == "__main__":
    main()
