# report-html —— 单文件 HTML 报告生成器（工作区级工具）

把一份或多份 Markdown 报告合并成**一个自包含 HTML**：左侧文档树（分组 + 全文搜索）+ 右侧内容面板。样式与脚本全部内嵌，无外部依赖、无第三方 Python 库，CJK 安全，生成后可直接发人。

对应工作区约定：「一个项目中的所有文档合并到一个 HTML 文件里，用文档树（左侧目录树/侧边栏导航）拆分展示各文档」。**今后项目的报告 HTML 用本工具生成，替代每次手写 HTML。**

```
用法：python3 build_report_html.py -i <md或目录>… | -m <清单.json>  -o <输出.html> [选项]
```

## 来源谱系

从 `projects/高尔夫智能设备调研/scripts/build_html.py` 泛化（该脚本是 15+ 份手写报告 HTML 中唯一可靠的生成器）：

- `md_to_html` / `inline` 两个函数**原样保留**（battle-tested 的最小 md 转换器：标题/表格/列表/加粗/链接/分隔线/引用/代码块）。
- 文档清单从硬编码的 `DOCS` 数组改为 CLI（`--input`）或清单文件（`--manifest`）提供。
- 按 `# ` 一级标题把单份 md 切成多章树节点的能力，吸收自高尔夫的 `build_final_html.py`（`split_chapters`）。
- 页面模板沿用高尔夫总览版式：`:root` 主题变量、侧边树、全文搜索（标题+正文命中、自动隐藏未命中分组）、移动端降级。高尔夫 CSS 里硬编码的三处颜色（引用背景/代码背景/高亮背景）提为变量 `--accent-soft` / `--code-bg` / `--mark-bg`，默认值不变。
- `build_deck_html.py` 是幻灯片（deck）生成器，走的是另一条版式路线，不在本工具范围内。

## 三种用法

### 1. 单份 md 按 `# ` 切章（终稿模式，等价于高尔夫 build_final_html.py）

```bash
python3 build_report_html.py \
  -i projects/XX项目/06-report/项目终稿.md --split \
  -o projects/XX项目/XX项目-终稿.html \
  --title "XX 项目 · 终稿" --subtitle "合并自 N 份过程文档"
```

每个 `# 一级标题` 成为一个树节点；首个 `#` 之前的前言成为第一个节点，节点名默认"封面"（`--cover-label` 可改）。若 md 本身第一行就是 `# 总标题`，则第一个节点自动以它命名。

### 2. 多份 md / 目录（总览模式，等价于高尔夫 build_html.py 的 DOCS 清单）

```bash
python3 build_report_html.py \
  -i projects/XX项目/05-整合文档 -i projects/XX项目/06-report/定价研究.md \
  -o projects/XX项目/XX项目-总览.html \
  --title "XX 项目 · 项目总览" --subtitle "验证 → 需求 → 市场"
```

- 每份 md = 一个树节点，节点标题取 md 内第一个 `# ` 标题，没有则用文件名。
- **目录输入**：递归收集 `*.md`（跳过隐藏文件/目录），按相对路径排序；一级子目录名自动成为分组标题（如 `05-整合文档/`、`06-report/`）。同一文件被多个 `--input` 覆盖时只收一次。
- 目录模式收多收全（含 `历史副本/` 等一切子目录）；要精确控制收录哪些文件、分组和顺序，用清单模式。

### 3. 清单模式（文件→树节点标题映射、分组、顺序、主题）

清单是一个 JSON 文件，推荐放在项目根（如 `XX项目/report-manifest.json`），`file` 相对路径基于清单所在目录：

```json
{
  "title": "XX 项目 · 项目总览",
  "subtitle": "验证 → 需求 → 市场\n第二行副标题",
  "output": "XX项目-总览.html",
  "theme": { "accent": "#0f5ea8", "accent-ink": "#0a3f73", "accent-soft": "#eaf2fb" },
  "docs": [
    { "group": "★ 整合交付" },
    { "title": "00 文档地图与阅读指引（先读这个）", "file": "05-整合文档/00-文档地图.md" },
    { "title": "01 BRD · 商业需求文档", "file": "05-整合文档/01-BRD.md" },
    { "title": "03 PRD · 产品需求文档（按章拆分）", "file": "05-整合文档/03-PRD.md", "split": true },
    { "group": "研究与验证" },
    { "file": "06-report/定价研究.md" }
  ]
}
```

```bash
python3 /Users/tongxiarui/Documents/AI\ app/codex/tools/report-html/build_report_html.py \
  -m projects/XX项目/report-manifest.json
```

- 顶层字段全部可选；也允许顶层直接是一个数组（只有 `docs`）。
- `docs` 两种条目：`{"group": "分组名"}` 插入一个分组标题；`{"file": …, "title": …, "split": …}` 一份文档——`title` 缺省取 md 首个 `# ` 标题或文件名，`split` 缺省继承 `--split` 或清单顶层 `"split": true`。
- `output` 相对路径基于清单所在目录；`--output` 可覆盖。
- 清单里指向的文件缺失时不中断：该节点渲染"缺失文件：路径"占位并告警到 stderr（与高尔夫版行为一致）。`--input` 指定的路径不存在则直接报错。

## CLI 一览

| 参数 | 说明 |
|---|---|
| `-i, --input PATH` | md 文件或目录，可重复；与 `--manifest` 二选一 |
| `-m, --manifest FILE` | 清单 JSON；与 `--input` 二选一 |
| `-o, --output FILE` | 输出 HTML 路径；缺省用清单的 `output` 字段 |
| `--title TEXT` | 页面主标题；缺省取清单 `title` 或输出文件名去后缀 |
| `--subtitle TEXT` | 侧栏品牌区副标题，支持 `\n` 换行；末尾自动附"构建日期 · N 篇文档" |
| `--split` | 每份 md 按 `# ` 一级标题切成多个树节点（清单可按文档覆盖） |
| `--theme K=V` | 覆盖 `:root` 主题变量，逗号分隔可重复；CLI 优先于清单 `theme` |
| `--root DIR` | 相对路径基准目录（`--input` 默认当前目录；清单 `file` 默认清单所在目录；清单文件本身的路径相对当前目录） |
| `--cover-label TEXT` | split 模式下首标题之前前言的节点名，默认"封面" |

## 主题定制

全部主题变量（`--theme` 与清单 `theme` 可覆盖任意子集）：

| 变量 | 默认（高尔夫绿） | 作用 |
|---|---|---|
| `--bg` | `#f7f7f5` | 页面背景 |
| `--panel` | `#ffffff` | 侧栏底色 |
| `--ink` | `#1a1a1a` | 正文 |
| `--sub` | `#6b6b6b` | 次要文字（分组标题、副标题） |
| `--line` | `#e4e4e0` | 分隔线、表格边框 |
| `--accent` | `#0f6b4f` | 强调色（激活左边条、引用竖线、搜索聚焦） |
| `--accent-ink` | `#0b4a37` | 强调色文字（标题、链接、激活项） |
| `--accent-soft` | `#eef5f1` | 强调色浅底（激活项背景、引用背景） |
| `--code-bg` | `#f0f0ec` | 行内代码 / 表头 / hover 背景 |
| `--mark-bg` | `#ffe9a8` | mark 高亮底色 |

蓝色主题示例（对齐脑机接口调研总览的观感）：

```bash
--theme "accent=#0f5ea8,accent-ink=#0a3f73,accent-soft=#eaf2fb,bg=#f7f8fa,line=#e4e7ee"
```

## 与手写实例的差异

工作区现有手写 HTML（脑机接口调研-总览、某消费品客户 deliverables 等）风格一致但各有定制。本工具输出的是**高尔夫总览版式的固定模板**，与手写实例的差别：

- **布局同构**：左侧品牌区 + 分组树 + 内容面板 + 移动端隐藏侧栏，均一致。
- **手写版多出的组件**：脑机版有 KPI 卡片、`.big` 结论块、时间线、可折叠分组（caret）、外链 `↗` 标记、`.file` 文件路径样式；某消费品客户版有深色侧栏、tag 徽章、KPI 卡。这些组件对应的内容不在 md 语法层，本工具不生成——需要这类"结论卡片/指标卡"的表达时，用 md 的表格或引用块近似，或对该页手写。
- **本工具多出的能力**：全文搜索框（标题+正文，命中自动跳转）、自动构建日期与文档计数、`--theme` 换肤。
- **样式细节**：默认浅色 + 绿色强调（高尔夫观感）；换蓝色后与脑机版观感接近，但分组不可折叠、正文最大宽度 980px。

## 支持的 md 语法与已知限制

`md_to_html` 是高尔夫项目沉淀的最小转换器，**刻意保持原行为**（含其怪癖），改它会改变 15+ 份历史报告的渲染口径。支持：`#`-`######` 标题（渲染为 h2-h6，整体降一级）、围栏代码块（忽略语言标记）、`---`/`***` 分隔线、`>` 引用、GFM 表格（忽略对齐冒号）、无序/有序列表、行内 `` `code` `` / `[链接](url)`（新窗口打开）/ `**加粗**` / `*斜体*`，其余行按段落。

已知限制（均为高尔夫版原有行为，非泛化引入）：

- **嵌套列表会拍平**：缩进的子列表项并入父列表同级。
- **引用不合并**：连续多行 `>` 渲染成多个相邻 blockquote（视觉上是分开的引用块）。
- **代码内星号会被误斜体**：行内代码里含 `*…*` 时可能被再处理成 `<em>`，极端情况下产生不配对标签（浏览器可正常渲染；现有高尔夫总览 HTML 同样如此）。源文件 `项目终稿-高尔夫智能硬件与IP.md` 可复现。
- **图片不支持**：`![alt](url)` 退化为 `!链接`；本工具面向纯文字报告。
- 不支持：表格对齐、删除线、脚注、任务列表、HTML 直通（会被转义）、Setext 式标题。
- 树分组只有一层；无 TOC 二级折叠。

## 后续项目怎么用（替代手写）

1. 项目内照常以 md 存档各文档（工作区只留 `.html` 展示件 + `.md` 存档件）。
2. 交付时在项目根放一份 `report-manifest.json`（分组、标题映射、顺序、主题），或直接用 `-i 目录` 快速出稿。
3. 生成命令在项目内留痕（写进 manifest 或 README），保证可重建：

```bash
python3 "/Users/tongxiarui/Documents/AI app/codex/tools/report-html/build_report_html.py" \
  -m "projects/<项目名>/report-manifest.json"
```

4. 输出 `<项目名>-总览.html` / `<项目名>-终稿.html` 到项目根，与高尔夫、脑机两项目的命名一致。
5. 特殊版式诉求（deck、深色侧栏、KPI 卡）仍手写——那是模板之外的定制，不要往本工具里塞。
