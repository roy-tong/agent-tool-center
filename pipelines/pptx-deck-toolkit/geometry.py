# -*- coding: utf-8 -*-
"""
geometry.py —— 统一版文本宽度估算 + 溢出/重叠检测核心。

纯标准库，不依赖 python-pptx（audit_deck.py 负责 pptx 侧的形状适配）。

┌─ text_w_pt 的三家实现对比结论（2026-10 抽样核对）─────────────────────────┐
│                                                                          │
│ 1. 项目甲 build_deck_v20.py      text_w_pt(text, size)：                    │
│    CJK(≥U+2E80)=1.0em / 空格=0.28em / 宽标点"·—×→↓↑"=0.9em / 其他=0.55em │
│    被 n_lines / fit_scale / 标签列宽自适应三处使用。                      │
│ 2. 项目甲 build_deck_v20_html.py  text_w_pt(text, size)：                    │
│    与 1 逐字节相同（注释自称"与 PPTX 渲染器一致"）。存在的意义是保证     │
│    HTML 预览与 PPTX 用同一套估算——复制是为了两边不漂移，但代价是改一处   │
│    要同步两处。                                                          │
│ 3. 项目甲 audit_deck_v20.py      tw(text, size)：                            │
│    同一套系数（1.0/0.28/0.9/0.55），只是缩写名、把 size*1.0 写成 size。   │
│    用于从已保存的 pptx 反推"需要的文本高度"。                             │
│ 4. 高尔夫 build_deck_pptx.py：  没有文本宽度估算。它的 qa() 只做包围盒    │
│    级检查（画布外 + 两两重叠面积比），文本是否装得下靠预留大框 + 肉眼。  │
│    （所以"高尔夫 build 重复实现 text_w_pt"的说法不成立，见 README。）     │
│                                                                          │
│ 结论：三处实现系数完全一致，无版本漂移——但重复本身就是漂移风险；          │
│ 统一版以项目甲 v20 build 的实现为底（它是唯一直正参与排版决策的一份），     │
│ 高尔夫谱系复用同一估算即可（估算与画布主题无关）。                        │
└──────────────────────────────────────────────────────────────────────────┘

其他从两家沉淀的几何规则：

- fit_scale 收缩阶梯（项目甲 build）：字号按 1.0→0.64 的 10 档收缩直到文本
  装进框，替代 PowerPoint 的 normAutofit（后者在不同查看器里行为不一致）。
- 行距下限 1.25em（项目甲 build）：低于它 Latin 下伸部（g/y/p）会被切掉。
- 行距语义（项目甲 build 的关键经验）：spcPct 是"单倍行距的百分比"，而 CJK
  字体单倍行距 ≈1.35–1.4em，会让实际行高比预期高约 35%；要用绝对值 spcPts
  （python-pptx 里设 Pt()），与 CSS line-height 语义一致。审计侧反读时：
  Length→.pt，float→视为 em 倍数乘基准字号，None→1.3 近似。
- 重叠判据（高尔夫 qa）：两框交叠 ox>0.06in 且 oy>0.06in 且交叠面积 >
  15% 小框面积，才算真重叠——比"有交就算"的朴素判据抗噪。
"""
from __future__ import annotations

import math
from typing import Dict, Iterable, Sequence, Tuple

__all__ = [
    "PX_PER_IN", "PT_PER_IN",
    "px2in", "px2pt", "in2pt", "pt2in",
    "text_w_pt", "n_lines", "fit_scale", "paras_need_h", "runs_lines",
    "intersect_wh", "overlap_area", "contains", "rect_area",
    "Rect", "MIN_LINE_SPACING", "DEFAULT_LS", "FIT_LADDER",
]

# ------------------------------------------------------------------ 单位
PX_PER_IN = 96.0     # 高尔夫/脑机接口谱系标尺：1280×720px = 13.33×7.5in
PT_PER_IN = 72.0


def px2in(px: float) -> float:
    return px / PX_PER_IN


def px2pt(px: float) -> float:
    return px * 0.75


def in2pt(v: float) -> float:
    return v * PT_PER_IN


def pt2in(v: float) -> float:
    return v / PT_PER_IN


# ------------------------------------------------------------------ 文本度量
# 统一版字符宽度系数（pt/em）。取自项目甲 v20 build_deck_v20.py 的 text_w_pt，
# 与 audit_deck_v20.tw、build_deck_v20_html.text_w_pt 系数一致（见模块 docstring）。
# 修正历史经验：CJK 全角 = 1em 是稳的；拉丁 0.55em 对 Hiragino Sans GB 偏保守
# （实测约 0.45-0.52em），保守方向正确——宁可多估宽度、多折一行，也不要低估。
WIDE_PUNCT = "·—×→←↓↑"      # 宽标点/箭头：0.9em（项目甲原集合只有 "·—×→↓↑"，
#                           # 统一版补上 ←（flywheel 块用到），系数不变）
CJK_THRESHOLD = 0x2E80           # CJK 部首起点；以上的 CJK/全角标点按 1em 计


def text_w_pt(text: str, size: float) -> float:
    """估算一行文本宽度（pt）。CJK 按 1em，空格 0.28em，宽标点 0.9em，其他 0.55em。

    与项目甲 v20 三处实现保持同一系数（见模块 docstring 的对比结论），
    因此审计结果与 build 期排版决策可比。"""
    w = 0.0
    for ch in text:
        o = ord(ch)
        if o >= CJK_THRESHOLD:
            w += size          # 等价于 size * 1.0（audit_deck_v20.tw 的写法）
        elif ch == " ":
            w += size * 0.28
        elif ch in WIDE_PUNCT:
            w += size * 0.9
        else:
            w += size * 0.55
    return w


def n_lines(text: str, size: float, w_in: float) -> int:
    """单一段落文本在 w_in 宽的框里占几行。"""
    if not text:
        return 1
    usable = max(w_in * PT_PER_IN, 1.0)
    return max(1, int(math.ceil(text_w_pt(text, size) / usable - 1e-6)))


def runs_lines(runs: Sequence[Tuple[str, float]], w_in: float) -> int:
    """混合字号的同段 runs 折行数。段内所有 run 宽度相加后再折行，
    不能逐 run 累加行数（项目甲 build.fit_scale 与 audit.need_h 的共同教训）。"""
    seg_w = sum(text_w_pt(t, s) for t, s in runs)
    usable = max(w_in * PT_PER_IN, 1.0)
    return max(1, int(math.ceil(seg_w / usable - 1e-6)))


# 收缩阶梯（项目甲 build.fit_scale 原样）：字号最多降到 0.64，再装不下就认了
FIT_LADDER = (1.0, 0.96, 0.92, 0.88, 0.84, 0.80, 0.76, 0.72, 0.68, 0.64)

MIN_LINE_SPACING = 1.25   # 行距下限：低于它 g/y/p 的下伸部会被切掉
DEFAULT_LS = 1.28         # 项目甲 build 正文默认行距


def fit_scale(paras: Sequence[Dict], w_in: float, h_in: float,
              ls: float = DEFAULT_LS, ladder: Iterable[float] = FIT_LADDER) -> float:
    """返回一个 <=1 的字号缩放系数，使整段文本装进 w×h（项目甲 build 原逻辑）。

    paras 形如 [{"runs": [(text, size, ...), ...], "space_before": pt?}, ...]，
    兼容项目甲 build 的 P()/PM() 产物；缺 runs 的空段按 body 字号计一行。
    """
    for k in ladder:
        total = 0.0
        for p in paras:
            runs = p.get("runs") or []
            if not runs:
                total += 12.0 * k * ls / PT_PER_IN
                continue
            base = max(r[1] for r in runs) * k
            lines = runs_lines([(r[0], r[1] * k) for r in runs], w_in)
            total += lines * base * ls / PT_PER_IN
            if p.get("space_before"):
                total += p["space_before"] / PT_PER_IN
        if total <= h_in + 0.005:
            return k
    return 0.6


def paras_need_h(paras: Sequence[Dict], w_in: float,
                 ls: float = DEFAULT_LS) -> float:
    """内容契约侧的"需要高度"（英寸）。paras 同 fit_scale 的输入。

    审计 pptx 时不要用这个——pptx 里存着真实行距，用 audit_deck 的
    shape_need_h（经 line_spacing 反读）更准。"""
    total = 0.0
    for p in paras:
        runs = p.get("runs") or []
        if not runs:
            total += 12.0 * ls / PT_PER_IN
            continue
        base = max(r[1] for r in runs)
        lines = runs_lines([(r[0], r[1]) for r in runs], w_in)
        lsp = p.get("line_spacing")
        lh_pt = base * (lsp if isinstance(lsp, float) else ls)
        total += lines * lh_pt / PT_PER_IN
        if p.get("space_before"):
            total += p["space_before"] / PT_PER_IN
    return total


# ------------------------------------------------------------------ 矩形运算
Rect = Tuple[float, float, float, float]   # (x, y, w, h)，英寸


def intersect_wh(a: Rect, b: Rect) -> Tuple[float, float]:
    """交叠宽高；无交叠返回 (0, 0)。（项目甲 audit.inter 原样）"""
    ox = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    oy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return (ox, oy) if ox > 0 and oy > 0 else (0.0, 0.0)


def overlap_area(a: Rect, b: Rect) -> float:
    ox, oy = intersect_wh(a, b)
    return ox * oy


def rect_area(a: Rect) -> float:
    return a[2] * a[3]


def contains(a: Rect, b: Rect, eps: float = 0.0) -> bool:
    """b 是否整个在 a 内（含 eps 容差）。用于"嵌套卡片是合法的"判据。"""
    return (b[0] >= a[0] - eps and b[1] >= a[1] - eps
            and b[0] + b[2] <= a[0] + a[2] + eps
            and b[1] + b[3] <= a[1] + a[3] + eps)


def is_real_overlap(a: Rect, b: Rect,
                    min_wh: float = 0.06, area_ratio: float = 0.15) -> bool:
    """高尔夫 qa 的重叠判据：交叠两边都 > min_wh 英寸，且交叠面积 >
    area_ratio × 较小框面积。抗"贴边/擦角"误报。"""
    ox, oy = intersect_wh(a, b)
    if ox <= min_wh or oy <= min_wh:
        return False
    return ox * oy > area_ratio * min(rect_area(a), rect_area(b))
