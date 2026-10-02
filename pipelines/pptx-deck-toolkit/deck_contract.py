# -*- coding: utf-8 -*-
"""
deck_contract.py —— python-pptx 直排 deck 的内容模块契约（规范化 + 遗留模块加载）。

“代码即内容源”模式里，content 模块（项目甲 deck_vN_content.py / 高尔夫 deck_content.py）
长期只是“一堆约定俗成的 dict”：字段名靠渲染器代码隐性定义，改错了只有渲染时才炸。
本模块把它规范化为一个可校验的契约对象：

    DeckContract
      ├── palette     色板（role -> "RRGGBB"）
      ├── geometry    画布与版式几何（英寸）
      ├── type_scale  字号阶梯（pt）
      ├── font        字体名（西文 + 中文同一字体，两家现状一致）
      ├── footer      页脚左侧文案
      └── slides: [SlideSpec]
              ├── kind: cover | content | closing
              ├── eyebrow / headline / lede / takeaway / notes
              ├── blocks: [BlockSpec(type, x, y, w, h, data)]
              └── raw    原始 dict 保底（契约没覆盖的字段不丢）

from_legacy() 把两家的既有 content 模块加载成 DeckContract：

  - 项目甲 v20 形状（deck_v20_content.py）：
      DECK + TOKENS + GEO + TYPE + FONT + FOOTER_LEFT，单位英寸 / pt，
      契约字段与之一一对应（这是契约的基准形状）。
  - 高尔夫形状（高尔夫智能设备调研/scripts/deck_content.py，源自脑机接口 deck 版式体系）：
      SLIDES + PALETTE + FOOTER + FONT，1280×720 px 标尺。
      页级字段做语义映射（section→eyebrow / title→headline / subtitle→lede /
      take→takeaway / notes→notes），版式原语（columns/rows/table/metrics/duo/barlist）
      收进单个 BlockSpec；原语内部数据保留 px 标尺不动（它们的布局参数在渲染器里，
      content 模块本身不带坐标，强行换算反而造假数据）。

契约只描述“内容与版式参数”，不渲染、不写文件。渲染归各家 build 脚本，
几何审计归 audit_deck.py。本模块只用标准库，不依赖 python-pptx。
"""
from __future__ import annotations

import importlib.util
import os
import sys
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "Palette", "Geometry", "TypeScale", "BlockSpec", "SlideSpec", "DeckContract",
    "Issue", "from_legacy", "validate", "describe",
]

# --------------------------------------------------------------------------
# 标准定义
# --------------------------------------------------------------------------

# 色板 role -> 语义。项目甲 v20 TOKENS 的键是全集（深浅双主题），高尔夫 PALETTE
# 是深色单主题子集，别名映射见 PALETTE_ALIASES。
PALETTE_ROLES = (
    "bg", "card", "border", "zebra", "tint", "tint_border",
    "ink", "body", "muted", "accent", "accent_d",
    "dark_bg", "dark_card", "dark_border", "white", "dark_text",
    # 高尔夫侧扩展 role（深色单主题下的次级文本 / 强调金 / 分隔线 / 表头底）
    "gold", "rule", "head",
)
PALETTE_ALIASES = {
    "soft": "body",    # 高尔夫"次级文本" = 项目甲"正文"语义位
    "mute": "muted",   # 高尔夫"最弱文本" = 项目甲"弱化文本"语义位
}

Palette = Dict[str, str]  # role -> "RRGGBB"（不带 #，与两家现状一致）


@dataclass
class Geometry:
    """画布与版式几何，单位英寸。默认值 = 项目甲 v20 GEO（契约基准）。"""
    slide_w: float = 13.3333
    slide_h: float = 7.5
    margin: float = 0.62
    content_w: float = 12.09
    eyebrow_y: float = 0.48
    headline_y: float = 0.80
    body_top: float = 1.60
    footer_y: float = 7.06
    gutter: float = 0.16

    @property
    def content_x(self) -> float:
        return self.margin

    @property
    def content_right(self) -> float:
        return self.margin + self.content_w


@dataclass
class TypeScale:
    """字号阶梯，单位 pt。默认值 = 项目甲 v20 TYPE。"""
    eyebrow: float = 12.0
    headline: float = 26.0
    lede: float = 15.0
    card_title: float = 16.0
    row_title: float = 14.5
    body: float = 13.0
    bar: float = 15.0
    big: float = 28.0
    caption: float = 11.5
    footer: float = 11.0


@dataclass
class BlockSpec:
    """一个版式块。项目甲谱系：type + 绝对坐标（英寸）；高尔夫谱系：type + 原语数据（px，坐标为 None）。"""
    type: str
    x: Optional[float] = None
    y: Optional[float] = None
    w: Optional[float] = None
    h: Optional[float] = None
    data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, b: Dict[str, Any]) -> "BlockSpec":
        """把项目甲式 block dict 拆成几何字段 + data。兼容 width 别名。"""
        d = dict(b)
        x = d.pop("x", None)
        y = d.pop("y", None)
        w = d.pop("w", d.pop("width", None))
        h = d.pop("h", None)
        return cls(type=d.pop("type"), x=x, y=y, w=w, h=h, data=d)

    def to_dict(self) -> Dict[str, Any]:
        d = {"type": self.type}
        for k in ("x", "y", "w", "h"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        d.update(self.data)
        return d


@dataclass
class SlideSpec:
    """一页。kind ∈ {cover, content, closing}；高尔夫的版式原语页归一为 content
    + 单个 block（type=原语名），原语名保留在 block.type 里可追溯。"""
    kind: str
    eyebrow: Optional[str] = None
    headline: Optional[str] = None
    lede: Optional[str] = None
    takeaway: Optional[str] = None          # 高尔夫 take（项目甲用 bar block 表达，留空）
    notes: Optional[str] = None             # 高尔夫讲者备注（项目甲 v20 无）
    blocks: List[BlockSpec] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeckContract:
    source: str = "unknown"                 # "unionpay_v20" | "golf" | ...
    palette: Palette = field(default_factory=dict)
    geometry: Geometry = field(default_factory=Geometry)
    type_scale: TypeScale = field(default_factory=TypeScale)
    font: str = ""
    footer: str = ""
    slides: List[SlideSpec] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def slide_count(self) -> int:
        return len(self.slides)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "palette": self.palette,
            "geometry": asdict(self.geometry),
            "type_scale": asdict(self.type_scale),
            "font": self.font,
            "footer": self.footer,
            "slides": [{"kind": s.kind, "eyebrow": s.eyebrow, "headline": s.headline,
                        "lede": s.lede, "takeaway": s.takeaway,
                        "blocks": [b.to_dict() for b in s.blocks]}
                       for s in self.slides],
            "meta": self.meta,
        }


# --------------------------------------------------------------------------
# 两家谱系的已知块类型与必填字段（来自各自渲染器必然读取的字段）
# --------------------------------------------------------------------------

# 项目甲 v20 BLOCK_RENDERERS 的 18 种块。值为“渲染器必然读取（无默认值兜底）”的最小字段集。
UNIONPAY_V20_BLOCKS: Dict[str, Tuple[str, ...]] = {
    "bar": ("text",),
    "caption": ("text",),
    "chips": ("items",),
    "chain_rows": ("rows",),
    "stats": ("items",),
    "cards": ("items",),
    "rows": ("items",),
    "placeholder_rows": ("items",),
    "twocol": ("left", "right"),
    "side_panel": ("title", "items"),
    "chain": ("items",),
    "timeline": ("items",),
    "flywheel": ("items",),
    "phase_panel": ("items",),
    "table": ("headers", "rows"),
    "layers": ("items",),
    "phones": ("items",),
    "roles": ("items",),
}

# 高尔夫 build_deck_pptx.py 的 6 种原语（脑机接口 deck 版式体系四原语 + duo/barlist）
GOLF_BLOCKS: Dict[str, Tuple[str, ...]] = {
    "columns": ("cols",),
    "rows": ("rows",),
    "table": ("table",),
    "metrics": ("metrics",),
    "duo": ("duos",),
    "barlist": ("bars",),
}

# 注意："rows" 和 "table" 两家重名但数据字段不同——项目甲 rows 块的数据在 items、
# 表格在 headers+rows；高尔夫两个原语的数据分别在 rows / table 键下。
# 校验时按"变体任一满足即可"处理，不能拿高尔夫的字段要求去卡项目甲的块（反之亦然）。
KNOWN_BLOCK_VARIANTS: Dict[str, List[Tuple[str, ...]]] = {}
for _tbl in (UNIONPAY_V20_BLOCKS, GOLF_BLOCKS):
    for _t, _fields in _tbl.items():
        KNOWN_BLOCK_VARIANTS.setdefault(_t, []).append(_fields)
KNOWN_BLOCKS = {t: v[0] for t, v in KNOWN_BLOCK_VARIANTS.items()}

# 高尔夫原语页归一为 content 后的 block.type 集合（用于校验“高尔夫块不带坐标是正常的”）
GOLF_PRIMITIVE_KINDS = set(GOLF_BLOCKS) | {"cover", "closing"}

SLIDE_KINDS = ("cover", "content", "closing")

PLACEHOLDER_MARKS = ("【待填】", "{N}")   # 前者是项目甲 v20 的未填数据约定；后者是页数占位符


# --------------------------------------------------------------------------
# from_legacy：加载两家 content 模块
# --------------------------------------------------------------------------

def _load_module(path: str):
    """按路径 import 一个 content 模块（不要求它在 sys.path 上）。"""
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    name = "_deck_contract_legacy_%d" % abs(hash(path))
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load: %s" % path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod          # dataclass/typing 自引用需要可解析的模块名
    spec.loader.exec_module(mod)
    return mod


def _norm_palette(d: Dict[str, str]) -> Palette:
    """合并别名（soft→body / mute→muted），去掉 '#' 前缀，统一大写。"""
    out: Palette = {}
    for k, v in (d or {}).items():
        v = str(v).lstrip("#").upper()
        out[PALETTE_ALIASES.get(k, k)] = v
    return out


def _unionpay_contract(mod) -> DeckContract:
    """项目甲 v20 形状：DECK + TOKENS + GEO + TYPE + FONT + FOOTER_LEFT。"""
    geo_d = getattr(mod, "GEO", None) or {}
    geo = Geometry(**{k: float(geo_d[k]) for k in Geometry.__dataclass_fields__ if k in geo_d})
    type_d = getattr(mod, "TYPE", None) or {}
    ts = TypeScale(**{k: float(type_d[k]) for k in TypeScale.__dataclass_fields__ if k in type_d})
    slides: List[SlideSpec] = []
    for raw in mod.DECK:
        kind = raw.get("kind", "content")
        blocks = [BlockSpec.from_dict(b) for b in raw.get("blocks", [])]
        slides.append(SlideSpec(
            kind=kind,
            eyebrow=raw.get("eyebrow"),
            headline=raw.get("headline") or raw.get("title"),   # cover/closing 用 title
            lede=raw.get("lede") or raw.get("sub") or raw.get("subtitle"),
            notes=raw.get("notes"),
            blocks=blocks,
            raw=dict(raw),
        ))
    return DeckContract(
        source="unionpay_v20",
        palette=_norm_palette(getattr(mod, "TOKENS", None) or {}),
        geometry=geo,
        type_scale=ts,
        font=getattr(mod, "FONT", "") or "",
        footer=getattr(mod, "FOOTER_LEFT", "") or "",
        slides=slides,
        meta={"module_vars": sorted(v for v in dir(mod)
                                    if not v.startswith("_")
                                    and v in ("DECK", "TOKENS", "GEO", "TYPE", "FONT", "FOOTER_LEFT"))},
    )


def _golf_contract(mod) -> DeckContract:
    """高尔夫形状：SLIDES + PALETTE + FOOTER + FONT（1280×720 px 标尺）。

    页级字段语义映射：section→eyebrow / title→headline / subtitle→lede /
    take→takeaway / warn→data["_warn"] / notes→notes。
    版式原语收进单 block；原语数据（cols/rows/table/...）保留 px 标尺原样。
    画布几何按 build_deck_pptx.py 的版式常数换算成英寸，type_scale 按 deck_content.py
    docstring 的字号标尺（标题 42px/副题 25px/正文 26-28px/结论条 26px）取 px*0.75=pt。
    """
    PX = 96.0
    geo = Geometry(
        slide_w=1280 / PX, slide_h=720 / PX,
        margin=64 / PX, content_w=1152 / PX,
        eyebrow_y=34 / PX, headline_y=79 / PX, body_top=230 / PX,
        footer_y=675 / PX,  # 页脚文字带（662px 分隔线之下），页码同带
        gutter=44 / PX,
    )
    ts = TypeScale(
        eyebrow=17 * 0.75, headline=42 * 0.75, lede=25 * 0.75,
        card_title=31 * 0.75, row_title=27 * 0.75, body=27 * 0.75,
        bar=26 * 0.75, big=60 * 0.75, caption=20 * 0.75, footer=14 * 0.75,
    )
    slides: List[SlideSpec] = []
    for raw in mod.SLIDES:
        kind = raw.get("kind", "content")
        if kind in ("cover", "closing"):
            spec = SlideSpec(
                kind=kind,
                eyebrow=raw.get("section"),
                headline=raw.get("title"),
                lede=raw.get("subtitle"),
                takeaway=raw.get("take"),
                notes=raw.get("notes"),
                blocks=[],
                raw=dict(raw),
            )
        else:
            data = {k: v for k, v in raw.items()
                    if k not in ("kind", "section", "title", "subtitle", "take", "warn", "notes")}
            if raw.get("warn"):
                data["_warn"] = True       # 结论条用警示色（gold 而非 accent）
            spec = SlideSpec(
                kind="content",
                eyebrow=raw.get("section"),
                headline=raw.get("title"),
                lede=raw.get("subtitle"),
                takeaway=raw.get("take"),
                notes=raw.get("notes"),
                blocks=[BlockSpec(type=kind, data=data)],   # 坐标留 None：布局在渲染器里
                raw=dict(raw),
            )
        slides.append(spec)
    return DeckContract(
        source="golf",
        palette=_norm_palette(getattr(mod, "PALETTE", None) or {}),
        geometry=geo,
        type_scale=ts,
        font=getattr(mod, "FONT", "") or "",
        footer=getattr(mod, "FOOTER", "") or "",
        slides=slides,
        meta={"unit": "px@1280x720 (原语数据未换算)", "px_per_inch": PX},
    )


def from_legacy(path: str) -> DeckContract:
    """加载一个遗留 content 模块并归一为 DeckContract。自动识别项目甲/高尔夫形状。"""
    mod = _load_module(path)
    if hasattr(mod, "DECK"):
        return _unionpay_contract(mod)
    if hasattr(mod, "SLIDES"):
        return _golf_contract(mod)
    raise ValueError(
        "%s 不是已知的 content 模块形状：既没有 DECK（项目甲），也没有 SLIDES（高尔夫）" % path
    )


# --------------------------------------------------------------------------
# 契约校验
# --------------------------------------------------------------------------

@dataclass
class Issue:
    level: str          # ERROR / WARN / INFO
    slide: int          # 1-based；0 = deck 级
    code: str
    message: str

    def __str__(self) -> str:
        where = "deck" if self.slide == 0 else "P%02d" % self.slide
        return "[%s/%s] %s: %s" % (self.level, self.code, where, self.message)


def _iter_text_fields(node: Any, path: str = ""):
    """递归产出 dict/list 里所有字符串字段（用于占位符扫描）。"""
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from _iter_text_fields(v, "%s.%s" % (path, k) if path else str(k))
    elif isinstance(node, (list, tuple)):
        for i, v in enumerate(node):
            yield from _iter_text_fields(v, "%s[%d]" % (path, i))


def validate(c: DeckContract,
             footer_band: float = 0.18,
             min_font_pt: float = 9.0) -> List[Issue]:
    """内容层静态校验。只查契约本身（不打开 pptx）：

    - 页 kind 与必备字段（cover/closing 要 title，content 要 headline）
    - 块类型已知、必填字段齐
    - 项目甲块缺 y/h（高尔夫原语块没有坐标是正常的，不报）
    - 块静态几何：y+h 压页脚带、同页块纵向重叠（近似全宽假设）
    - 占位符【待填】/页数 {N}
    - 字号阶梯里低于可读下限的值
    """
    issues: List[Issue] = []
    if not c.font:
        issues.append(Issue("WARN", 0, "font-missing", "契约未声明字体"))
    if not c.palette:
        issues.append(Issue("WARN", 0, "palette-missing", "契约未声明色板"))

    for role, v in c.type_scale.__dict__.items():
        if v and v < min_font_pt:
            issues.append(Issue("WARN", 0, "type-scale",
                                "字号阶梯 %s=%.1fpt 低于可读下限 %.1fpt" % (role, v, min_font_pt)))

    g = c.geometry
    for i, s in enumerate(c.slides, start=1):
        if s.kind not in SLIDE_KINDS:
            issues.append(Issue("ERROR", i, "slide-kind", "未知页 kind=%r" % s.kind))
        if s.kind in ("cover", "closing") and not (s.headline or s.raw.get("title")):
            issues.append(Issue("ERROR", i, "slide-field", "%s 页缺 title" % s.kind))
        if s.kind == "content" and not s.headline:
            issues.append(Issue("ERROR", i, "slide-field", "content 页缺 headline"))
        for path, text in _iter_text_fields(s.raw):
            for mark in PLACEHOLDER_MARKS:
                if mark in text:
                    issues.append(Issue("INFO", i, "placeholder",
                                        "%s 含 %s（页数占位符需渲染时替换，待填数据需补齐）" % (path, mark)))

        # 块级检查
        spans = []
        for b in s.blocks:
            if b.type not in KNOWN_BLOCK_VARIANTS:
                issues.append(Issue("WARN", i, "block-type",
                                    "未知块类型 %r（两家渲染器都不认识）" % b.type))
            else:
                # 重名块（rows/table）按变体校验：任一谱系的必填字段集满足即可
                ok_variants = [v for v in KNOWN_BLOCK_VARIANTS[b.type]
                               if all(k in b.data for k in v)]
                if not ok_variants:
                    expect = " 或 ".join("+".join(v) for v in KNOWN_BLOCK_VARIANTS[b.type])
                    issues.append(Issue("ERROR", i, "block-field",
                                        "块 %s 缺必填字段（期望 %s）" % (b.type, expect)))
            golf_like = b.type in GOLF_BLOCKS and b.y is None
            if not golf_like and (b.y is None or b.h is None):
                issues.append(Issue("WARN", i, "block-geom",
                                    "块 %s 缺 y/h 绝对坐标（高尔夫式原语则忽略）" % b.type))
            if b.y is not None and b.h is not None:
                bottom = b.y + b.h
                if bottom > g.footer_y - footer_band + 1e-9 and s.kind == "content":
                    issues.append(Issue("ERROR", i, "block-footer",
                                        "块 %s 底边 %.2f 压进页脚带（footer_y=%.2f）" % (b.type, bottom, g.footer_y)))
                if bottom > g.slide_h + 1e-9:
                    issues.append(Issue("ERROR", i, "block-canvas",
                                        "块 %s 底边 %.2f 超出画布高 %.2f" % (b.type, bottom, g.slide_h)))
                x0 = b.x if b.x is not None else g.content_x
                w = b.w if b.w is not None else g.content_w
                spans.append((x0, b.y, x0 + w, bottom, b.type))
        # 同页块两两重叠（近似：横区间有交集且纵向交 > 0.03in 就报；斑马/背景无法在内容层区分，降级 WARN）
        for a in range(len(spans)):
            for bb in range(a + 1, len(spans)):
                ax0, ay0, ax1, ay1, at = spans[a]
                bx0, by0, bx1, by1, bt = spans[bb]
                ox = min(ax1, bx1) - max(ax0, bx0)
                oy = min(ay1, by1) - max(ay0, by0)
                if ox > 0.05 and oy > 0.05:
                    issues.append(Issue("WARN", i, "block-overlap",
                                        "块 %s 与 %s 声明的矩形重叠 %.2fx%.2f in" % (at, bt, ox, oy)))
    return issues


def describe(c: DeckContract) -> str:
    """契约的人类可读摘要（一行一页）。"""
    lines = ["deck contract · source=%s · font=%s · footer=%r · %d 页"
             % (c.source, c.font, c.footer, c.slide_count),
             "geometry: %s" % c.geometry,
             "type_scale: %s" % c.type_scale,
             "palette: %d roles" % len(c.palette)]
    for i, s in enumerate(c.slides, start=1):
        head = s.headline or ""
        blocks = " ".join(b.type for b in s.blocks) or "-"
        extra = []
        if s.takeaway:
            extra.append("take")
        if s.notes:
            extra.append("notes")
        lines.append("P%02d %-8s %-14s %s%s" % (
            i, s.kind, "[" + blocks + "]" if blocks != "-" else "-",
            (head[:34] + "…") if len(head) > 34 else head,
            (" (" + ",".join(extra) + ")") if extra else ""))
    return "\n".join(lines)


if __name__ == "__main__":
    # python deck_contract.py <content.py> —— 快速查看契约归一结果
    if len(sys.argv) != 2:
        print("usage: python deck_contract.py <content_module.py>", file=sys.stderr)
        sys.exit(2)
    contract = from_legacy(sys.argv[1])
    print(describe(contract))
    problems = validate(contract)
    print("\n契约校验 %d 条：" % len(problems))
    for it in sorted(problems, key=lambda x: (x.slide, x.code)):
        print(" ", it)
