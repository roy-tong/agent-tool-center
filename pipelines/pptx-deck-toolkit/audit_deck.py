#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_deck.py —— python-pptx 直排 deck 的几何审计器 CLI。

两种输入：

  1) pptx 模式（主用）：对已生成的 pptx 做几何与排版审计
        python audit_deck.py path/to/deck.pptx
     检查项（项目甲 audit_deck_v20 为主干，吸收高尔夫 qa 与字号一致性检查）：
       C1 off-canvas     画布外（高尔夫 qa 吸收；装饰性出血形状可配排除）
       C2 margin         横向越界（内容出安全边距）
       C3 footer         压到页脚带
       C4 overflow       文本超出自身文本框（用统一 text_w_pt 反推需要高度）
       C5 escape-card    文本跑出所属卡片
       C6 foreign-card   文本压到"别人的"卡片（P07/P15 那类致命错位）
       C7 card-overlap   卡片之间重叠（排除斑马纹背景层与合法嵌套）
       C8 text-overlap   文本框两两重叠（高尔夫 qa 的面积比判据，默认 WARN）
       C9 bottom-gap     内容底边与页脚之间安全间距不足
       C10 font          字号一致性（页脚带字号统一 / 最小字号下限 / 孤立字号 /
                         字体种类）

  2) content 模式：内容契约校验（不打开 pptx）
        python audit_deck.py --content path/to/deck_vN_content.py
     即 deck_contract.from_legacy() + validate()。

刻意设计的豁免（继承项目甲 v20 的"真问题 vs 刻意设计"区分）：
  - 页脚带内的形状不参与越界/溢出/卡片检查；
  - 深色页（默认首末页）上 Oval 开头的装饰圆豁免；
  - 实心全宽浅色填充视为斑马纹背景层，不算卡片。

退出码：有 ERROR → 1；--strict 时 WARN/INFO 也计入；无问题 → 0。
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pptx import Presentation
from pptx.util import Emu

import deck_contract
import geometry
from deck_contract import DeckContract, Issue

EPS = 0.02   # 项目甲 v20 audit 的通用容差（英寸）

# 默认版式参数 = 项目甲 v20（契约基准）。高尔夫 deck 用
#   --slide-w 13.333 --margin 0.667 --footer-y 6.90 覆盖（662px 页脚分隔线）。
DEFAULTS = dict(slide_w=13.3333, slide_h=7.5, margin=0.62, footer_y=7.00)


def I(v) -> float:
    """EMU → 英寸。"""
    return Emu(v).inches


# ------------------------------------------------------------------ 形状侧适配
def fill_of(sh) -> Optional[str]:
    """实心填充色（RRGGBB），非实心/读不出 → None。（项目甲 audit.fill_of 原样）"""
    try:
        if sh.fill.type == 1:
            return str(sh.fill.fore_color.rgb)
    except Exception:
        pass
    return None


def shape_need_h(sh) -> float:
    """按统一 text_w_pt 反推该文本框"需要的高度"（英寸）。

    行距反读规则（项目甲 audit.need_h 原样，语义注释见 geometry 模块 docstring）：
    绝对值（Length/spcPts）优先读 .pt；百分比（float/spcPct）按 em 倍数乘基准
    字号；缺失按 1.3 近似（CJK 单倍行距经验值）。"""
    if not sh.has_text_frame:
        return 0.0
    w = I(sh.width)
    tot = 0.0
    for p in sh.text_frame.paragraphs:
        if not p.runs:
            continue
        sizes = [r.font.size.pt for r in p.runs if r.font.size]
        base = max(sizes) if sizes else 12.0
        lines = geometry.runs_lines(
            [(r.text, r.font.size.pt if r.font.size else base) for r in p.runs], w)
        lsp = p.line_spacing
        if lsp is None:
            lh_pt = base * 1.3
        elif isinstance(lsp, float):
            lh_pt = base * lsp
        else:
            lh_pt = lsp.pt
        sb = p.space_before.pt if p.space_before else 0.0
        tot += lines * lh_pt / geometry.PT_PER_IN + sb / geometry.PT_PER_IN
    return tot


class ShapeInfo:
    __slots__ = ("sh", "name", "r", "text", "txt", "fill", "footer", "deco", "bg", "sizes", "fonts")

    def __init__(self, sh, footer: bool, deco: bool, bg: bool):
        self.sh = sh
        self.name = sh.name
        self.r: geometry.Rect = (I(sh.left), I(sh.top), I(sh.width), I(sh.height))
        txt = sh.text_frame.text.strip() if sh.has_text_frame else ""
        self.txt = txt
        self.text = bool(txt)
        self.fill = fill_of(sh)
        self.footer = footer
        self.deco = deco
        self.bg = bg          # 满幅实心背景矩形（高尔夫谱系画成形状；项目甲是幻灯片背景属性）
        self.sizes: List[float] = []
        self.fonts: List[Optional[str]] = []
        if sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                for run in p.runs:
                    self.sizes.append(run.font.size.pt if run.font.size else None)  # type: ignore[arg-type]
                    self.fonts.append(run.font.name)


def collect_shapes(slide, idx: int, n_slides: int, opt) -> List[ShapeInfo]:
    dark = idx in opt.dark_slide_set(n_slides)
    items = []
    for sh in slide.shapes:
        try:
            top = I(sh.top)
        except Exception:
            continue
        footer = top >= opt.footer_y
        deco = dark and sh.name.startswith(opt.deco_prefix)
        # 满幅实心矩形 = 页面背景（高尔夫谱系），豁免越界/页脚/卡片检查
        try:
            bg = (fill_of(sh) is not None
                  and I(sh.width) >= opt.slide_w - 2 * EPS
                  and I(sh.height) >= opt.slide_h - 2 * EPS)
        except Exception:
            bg = False
        items.append(ShapeInfo(sh, footer, deco, bg))
    return items


# ------------------------------------------------------------------ pptx 审计
def audit_pptx(path: str, opt) -> List[Issue]:
    prs = Presentation(path)
    issues: List[Issue] = []
    footer_sizes: Counter = Counter()
    all_sizes: Counter = Counter()
    all_fonts: Counter = Counter()

    def add(level, slide, code, msg):
        issues.append(Issue(level, slide, code, msg))

    for idx, slide in enumerate(prs.slides, start=1):
        items = collect_shapes(slide, idx, len(prs.slides), opt)
        dark = idx in opt.dark_slide_set(len(prs.slides))

        # ---- C1 画布外 / C2 横向越界 / C3 压页脚带（项目甲 check1 + golf out）
        for s in items:
            if s.deco or s.bg:
                continue
            x, y, w, h = s.r
            if (not s.footer and (x < -EPS or y < -EPS
                                  or x + w > opt.slide_w + EPS
                                  or y + h > opt.slide_h + EPS)):
                add("ERROR" if not opt.allow_bleed else "WARN", idx, "off-canvas",
                    '%s (%.2f,%.2f %.2fx%.2f) 超出画布 %.2fx%.2f :: %r'
                    % (s.name, x, y, w, h, opt.slide_w, opt.slide_h, s.txt[:22]))
            if s.footer:
                continue
            if x < opt.margin - EPS or x + w > opt.slide_w - opt.margin + EPS:
                add("ERROR", idx, "margin",
                    '%s x=%.2f 右=%.2f（安全边距 %.2f）:: %r'
                    % (s.name, x, x + w, opt.margin, s.txt[:22]))
            if y + h > opt.footer_y + EPS:
                add("ERROR", idx, "footer",
                    '%s 底=%.2f 压到页脚带（footer_y=%.2f）:: %r'
                    % (s.name, y + h, opt.footer_y, s.txt[:26]))

        # ---- C4 文本超出自身文本框（项目甲 check2）
        for s in items:
            if not s.text or s.footer:
                continue
            nh = shape_need_h(s.sh)
            if nh > s.r[3] + 0.08:
                add("ERROR", idx, "overflow",
                    '%s 需≈%.2f 框=%.2f @(%.2f,%.2f) :: %r'
                    % (s.name, nh, s.r[3], s.r[0], s.r[1], s.txt[:26]))

        # ---- 卡片识别（项目甲 check3 前置）：实心、无文本、够大、非装饰；
        #      背景/斑马纹填充色不算卡片
        bg_set = {c.upper().lstrip("#") for c in opt.bg_fills}
        cards = [s for s in items
                 if s.fill and not s.text and not s.bg
                 and s.r[2] > opt.card_min_w and s.r[3] > opt.card_min_h
                 and not s.deco and s.fill.upper() not in bg_set]

        # ---- C5 文本跑出所属卡片（项目甲 3a：以左上角+0.03 认主，取最小容器）
        for s in items:
            if not s.text or s.footer:
                continue
            x, y, w, h = s.r
            cx, cy = x + 0.03, y + 0.03
            owners = [c for c in cards
                      if c.r[0] - EPS <= cx <= c.r[0] + c.r[2] + EPS
                      and c.r[1] - EPS <= cy <= c.r[1] + c.r[3] + EPS]
            if not owners:
                continue
            p = min(owners, key=lambda c: geometry.rect_area(c.r))
            px, py, pw, ph = p.r
            if (x + w > px + pw + 0.02 or y + h > py + ph + 0.02
                    or x < px - 0.02 or y < py - 0.02):
                add("ERROR", idx, "escape-card",
                    '%s 越出 %s(%.2f,%.2f,%.2fx%.2f) :: %r'
                    % (s.name, p.name, px, py, pw, ph, s.txt[:22]))

        # ---- C6 文本压到"别人的"卡片（项目甲 3b）
        for s in items:
            if not s.text or s.footer:
                continue
            cx, cy = s.r[0] + 0.03, s.r[1] + 0.03
            inside = any(c.r[0] - EPS <= cx <= c.r[0] + c.r[2] + EPS
                         and c.r[1] - EPS <= cy <= c.r[1] + c.r[3] + EPS
                         for c in cards)
            if inside:
                continue
            for c in cards:
                ox, oy = geometry.intersect_wh(s.r, c.r)
                if ox > 0.05 and oy > 0.05:
                    add("ERROR", idx, "foreign-card",
                        '%s :: %r 与 %s(%.2f,%.2f) 重叠 %.2fx%.2f'
                        % (s.name, s.txt[:22], c.name, c.r[0], c.r[1], ox, oy))

        # ---- C7 卡片之间重叠（项目甲 4；嵌套豁免）
        for i in range(len(cards)):
            for j in range(i + 1, len(cards)):
                a, b = cards[i], cards[j]
                if geometry.contains(a.r, b.r, EPS) or geometry.contains(b.r, a.r, EPS):
                    continue
                ox, oy = geometry.intersect_wh(a.r, b.r)
                if ox > 0.03 and oy > 0.03 and ox * oy > 0.02:
                    add("ERROR", idx, "card-overlap",
                        '%s 与 %s 重叠 %.2fx%.2f' % (a.name, b.name, ox, oy))

        # ---- C8 文本框两两重叠（高尔夫 qa；项目甲排版常把文本压在自己的卡片上，
        #      但文本压文本几乎必错 → 仍设 WARN 而非 ERROR，可用 --text-overlap-ratio 调）
        tboxes = [s for s in items if s.text and not s.deco]
        for i in range(len(tboxes)):
            for j in range(i + 1, len(tboxes)):
                a, b = tboxes[i], tboxes[j]
                if opt.text_overlap_enabled and geometry.is_real_overlap(
                        a.r, b.r, 0.06, opt.text_overlap_ratio):
                    add("WARN", idx, "text-overlap",
                        '%r × %r 交叠 %.2fx%.2f in'
                        % (a.txt[:12], b.txt[:12],
                           *geometry.intersect_wh(a.r, b.r)))

        # ---- C9 底部留白（项目甲 5；首末页深色页豁免）
        if idx not in (1, len(prs.slides)):
            body = [s for s in items if s.text and not s.footer and not s.deco]
            if body:
                low = max(s.r[1] + s.r[3] for s in body)
                if opt.footer_y - 0.18 < low <= opt.footer_y:
                    add("WARN", idx, "bottom-gap",
                        '内容最低点 %.2f 距页脚线 %.2f 不足 0.18 in' % (low, opt.footer_y))

        # ---- C10 字号/字体收集（页脚带字号在循环外汇总判定）
        for s in items:
            for sz in s.sizes:
                if sz is None:
                    continue
                all_sizes[round(sz, 1)] += 1
                if s.footer:
                    footer_sizes[round(sz, 1)] += 1
            for f in s.fonts:
                all_fonts[f or "(inherit)"] += 1

    # ---- C10 汇总判定
    if len(footer_sizes) > 1:
        issues.append(Issue("WARN", 0, "font-footer",
                            "页脚带出现多种字号: %s" % dict(footer_sizes)))
    tiny = {sz: n for sz, n in all_sizes.items() if sz < opt.min_font}
    if tiny:
        issues.append(Issue("WARN", 0, "font-min",
                            "存在低于 %.1fpt 的字号: %s" % (opt.min_font, tiny)))
    rare = {sz: n for sz, n in all_sizes.items() if n <= 2}
    if rare and len(all_sizes) > 4:
        issues.append(Issue("INFO", 0, "font-rare",
                            "孤立字号（全 deck 仅 ≤2 个 run 使用）: %s" % rare))
    if len(all_fonts) > 2:
        issues.append(Issue("INFO", 0, "font-mix",
                            "混用多种字体: %s" % dict(all_fonts)))
    return issues


# ------------------------------------------------------------------ 输出
def print_issues(issues: List[Issue], title: str) -> Tuple[int, int, int]:
    n_err = sum(1 for i in issues if i.level == "ERROR")
    n_warn = sum(1 for i in issues if i.level == "WARN")
    n_info = sum(1 for i in issues if i.level == "INFO")
    print("== %s ==" % title)
    print("共 %d 条（ERROR %d / WARN %d / INFO %d）\n" % (len(issues), n_err, n_warn, n_info))
    cur = None
    for it in sorted(issues, key=lambda x: (x.slide, x.code, x.message)):
        if it.slide != cur:
            print("--- %s ---" % ("deck 级" if it.slide == 0 else "P%02d" % it.slide))
            cur = it.slide
        print("  %s" % it)
    return n_err, n_warn, n_info


class Opt:
    """argparse 结果 + dark_slide_set 便捷方法。"""

    def __init__(self, args):
        self.slide_w = args.slide_w
        self.slide_h = args.slide_h
        self.margin = args.margin
        self.footer_y = args.footer_y
        self.bg_fills = args.bg_fill.split(",") if args.bg_fill else []
        self.card_min_w = args.card_min_w
        self.card_min_h = args.card_min_h
        self.deco_prefix = args.deco_prefix
        self.allow_bleed = args.allow_bleed
        self.text_overlap_enabled = not args.no_text_overlap
        self.text_overlap_ratio = args.text_overlap_ratio
        self.min_font = args.min_font
        self._dark = args.dark_slides
        self._dark_cache = None

    def dark_slide_set(self, n: int):
        if self._dark_cache is None:
            if self._dark == "auto":
                s = {1, n} if n else set()
            elif self._dark == "none":
                s = set()
            else:
                s = set()
                for part in self._dark.split(","):
                    part = part.strip()
                    if not part:
                        continue
                    if "-" in part:
                        a, b = part.split("-", 1)
                        s.update(range(int(a), int(b) + 1))
                    else:
                        s.add(int(part))
            self._dark_cache = s
        return self._dark_cache


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="python-pptx 直排 deck 几何审计器（项目甲 v20 audit + 高尔夫 qa 吸收合并）")
    ap.add_argument("pptx", nargs="?", help="待审计的 .pptx 文件")
    ap.add_argument("--content", help="内容契约校验模式：传入 content 模块路径（项目甲 deck_vN_content.py 或高尔夫 deck_content.py）")
    ap.add_argument("--slide-w", type=float, default=DEFAULTS["slide_w"])
    ap.add_argument("--slide-h", type=float, default=DEFAULTS["slide_h"])
    ap.add_argument("--margin", type=float, default=DEFAULTS["margin"],
                    help="内容安全边距（英寸）；高尔夫 deck 用 0.667")
    ap.add_argument("--footer-y", type=float, default=DEFAULTS["footer_y"],
                    help="页脚带上沿（英寸）；高尔夫 deck 用 6.75")
    ap.add_argument("--bg-fill", default="F4F1EB",
                    help="背景/斑马纹填充色，逗号分隔（这些不算卡片）")
    ap.add_argument("--card-min-w", type=float, default=1.2, help="卡片最小宽（英寸）")
    ap.add_argument("--card-min-h", type=float, default=0.40, help="卡片最小高（英寸）")
    ap.add_argument("--dark-slides", default="auto",
                    help="深色页页码：auto=首末页 | none | 逗号分隔页码/区间")
    ap.add_argument("--deco-prefix", default="Oval", help="深色页装饰形状名前缀（豁免画布外）")
    ap.add_argument("--allow-bleed", action="store_true", help="画布外出血降为 WARN（封面大圆等刻意出血）")
    ap.add_argument("--no-text-overlap", action="store_true", help="关闭 C8 文本两两重叠检查")
    ap.add_argument("--text-overlap-ratio", type=float, default=0.15,
                    help="C8 面积比阈值（交叠面积/较小框面积）")
    ap.add_argument("--min-font", type=float, default=9.0, help="最小字号下限（pt）")
    ap.add_argument("--json", help="问题清单同时写一份 JSON")
    ap.add_argument("--strict", action="store_true", help="WARN/INFO 也计入退出码")
    args = ap.parse_args(argv)

    if not args.pptx and not args.content:
        ap.error("需要 pptx 文件或 --content 模块路径之一")

    issues: List[Issue] = []
    if args.content:
        try:
            contract = deck_contract.from_legacy(args.content)
        except Exception as e:
            print("契约加载失败：%s" % e, file=sys.stderr)
            return 2
        print(deck_contract.describe(contract))
        print()
        issues = deck_contract.validate(contract)
        n_err, n_warn, n_info = print_issues(issues, "content 契约审计 %s" % args.content)
    else:
        if not os.path.isfile(args.pptx):
            print("文件不存在：%s" % args.pptx, file=sys.stderr)
            return 2
        opt = Opt(args)
        issues = audit_pptx(args.pptx, opt)
        n_err, n_warn, n_info = print_issues(issues, "pptx 几何审计 %s" % args.pptx)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump([{"level": i.level, "slide": i.slide, "code": i.code,
                        "message": i.message} for i in issues],
                      f, ensure_ascii=False, indent=1)
        print("\nJSON 已写入 %s" % args.json)

    if n_err:
        return 1
    if args.strict and (n_warn or n_info):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
