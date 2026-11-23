# Deck 生产架构：成熟生成器 + 内容/视觉锁 + 双重审计

用于实际 PPTX、PDF、HTML deck 的生成、编辑、导出与验收。文案和事实仍由 `my-voice / deck-humanizer` 负责，设计决策由 `deck-design` 负责；本文件决定**在 my-voice 工作流中选用哪条生产链**。研究核对日期：2026-11-22。

## 一、默认架构

```text
my-voice / deck-humanizer：叙事、事实、中文与英文文案
        ↓
content-lock：读者、页序、逐页主张、必须出现的证据、来源、备注
visual-lock：主题、字体、网格、组件、图表 token、导出目标
        ↓
Slidev 或 Presenton：生成、编辑、渲染、导出
        ↓
pptx-deck-toolkit：实际 PPTX 的内容契约与 C1–C10 几何审计
        ↓
实际 PPTX/PDF 渲染为 PNG：人工视觉复核与返修
```

保留内容锁、视觉锁和审计器，不再为新项目扩展自建 Vite/React 工具栏、本地存储和浏览器导出脚本。`deck-design` 在 my-voice 工作流中输出设计决策、主题/模板和组件契约；需要执行其旧 python-pptx 路径时，只用于下文的存量或高度定制场景。

## 二、工具路由

| 场景 | 默认选择 | 能交付什么 | 关键边界 |
| --- | --- | --- | --- |
| 新代码型 Deck、需要版本管理与组件复用 | **Slidev** | HTML、PDF、PNG、图片型 PPTX、可编辑 PPTX；CLI 支持 `pptx-editable` | 图片型 PPTX 最忠实但文字不可选；可编辑模式会重建形状，部分元素栅格化或整页回退，必须检查 |
| 普通用户需要 GUI、模板、拖拽编辑或可编辑 PPTX | **Presenton** | 桌面/Docker、模板、AI/API、编辑、可编辑 PPTX/PDF | AI 生成不等于事实正确或设计合格；仍须经过内容锁、事实核验和实际导出审计 |
| 简单 Markdown 演示、轻量转换 | **Marp**（备选） | MIT；Markdown → HTML/PDF/PPTX/图片 | `--pptx-editable` 是实验特性，需浏览器和 LibreOffice；还原度较低且不支持讲者备注，不作为高保真融资 BP 默认 |
| 存量 python-pptx 项目、复杂原生图表或明确需要逐对象控制 | **deck-design + python-pptx** | 原生可编辑 PPTX、既有图表和构建函数 | 不再为了可复制旧工程而新建自有 UI；仍执行同一内容/视觉锁和审计 |
| 存量 `deck-scaffold` 项目维护 | **仅兼容** | 维护既有工程与交付 | 不用于新 Deck，不继续扩展自有工具栏、本地存储、浏览器导出脚本 |
| 独立高交互网页或特殊 HTML 展示 | `impeccable`（按需） | 网页视觉与交互 | 不把它当默认 PPT 生产器；PPT 导出和审计仍走上述路由 |

`presentations:pptx` 等文件工具按环境用于读取、转换和渲染；不可用时报告缺口，不假装调用。工具存在不等于已完成验收。

## 三、内容锁与视觉锁

### `content-lock`

每页至少保留：

- 读者问题、唯一主张、证据角色。
- 必须出现的事实、数字、时间、分母、来源和实际/推算/目标标签。
- 主图与辅助模块、最重要限制、讲者备注和可能追问。
- 禁止出现的内容、已淘汰案例、不得混用的统计口径。

改内容先改锁，再改 Slidev Markdown、Presenton 项目或 python-pptx 内容源；不在导出的 PPTX 上临时改一处而忘了正本。

### `visual-lock`

固定：

- 画布、主题、字体与回退字体、网格、字号层级、色彩 token。
- 页型与组件、图表样式、来源/页脚、实际与目标的视觉区分。
- 导出目标：视觉保真优先还是逐对象可编辑优先。
- 不允许的组件、复杂效果和 PowerPoint 无等价物。

视觉锁不能让文字低于可读下限，也不能把必要证据删掉来适配模板。

## 四、导出模式按用途选择

| 用途 | 推荐 | 必须说明与检查 |
| --- | --- | --- |
| 只展示、保持浏览器视觉效果 | PDF / PNG / 图片型 PPTX | 图片型 PPTX 的文字不可选、元素不可逐项编辑，不能写成“原生可编辑” |
| 收件人要改文字、移动框、改颜色 | Slidev `pptx-editable` 或 Presenton 可编辑 PPTX | 重新打开检查文本是否可选、形状是否可编辑、哪些元素被栅格化或整页回退 |
| 需要讲者备注 | 选支持备注的导出路径 | 逐页核对备注是否保留；Marp 实验性可编辑导出明确不支持备注 |
| 含 Mermaid、SVG、canvas、视频、公式、复杂 CSS | 先决定保真还是可编辑 | Slidev 会将 PowerPoint 无等价物的元素留为图片，必要时整页回退；不能承诺全元素原生 |
| 字体跨机器交付 | 安装/提供合规字体或改用通用字体 | `.pptx` 只引用字体名，不嵌入字体；必须检查接收端替换和折行 |

## 五、验收顺序：源预览不能代替成品复核

1. **内容校验**：内容锁、事实、页序、数字、来源、待补位和备注完整；禁止项未回潮。
2. **源渲染检查**：检查 Slidev/Presenton 预览的组件、图表和基础布局。这里通过不代表 PPTX 通过。
3. **实际导出**：生成用户要求的 PPTX/PDF/HTML，记录工具、版本、导出模式和警告。
4. **静态与几何审计**：环境里存在 `pptx-deck-toolkit` 时，对实际 PPTX 执行内容契约与 C1–C10；检查越界、溢出、卡片重叠、压页脚、字号和字体。
5. **实际成品渲染**：将导出的 PPTX/PDF 再渲染为逐页 PNG，先看 contact sheet，再看关键页原尺寸。不能只验浏览器里的源页面。
6. **人工复核**：重点看字体替换、折行变化、文本溢出、图表标签、图片回退、页面空白、来源和页脚。
7. **文件回读**：重新打开 PPTX/PDF，核对页数、备注、图表值、可编辑性、字体和链接；所有警告已处理或明确披露。
8. **完整回归**：任何修改都回到内容/视觉锁或模板源，再执行导出、审计和渲染；不直接修 PNG 或只在成品上掩盖问题。

### 为什么两道检查都保留

[Slidev 官方](https://sli.dev/guide/exporting.html)明确说明：可编辑 PPTX 是在浏览器中测量后重建为 PowerPoint 形状；PowerPoint 的文本测量与浏览器不同，长段落可能换成不同行数，字体也需要接收端安装。几何审计能系统发现对象问题，真实 PNG 能发现字体、折行和渲染差异；二者互补，缺一都不能宣布验收完成。

## 六、官方依据

- [Slidev Exporting](https://sli.dev/guide/exporting.html)：PDF、PPTX、PNG、Markdown；浏览器导出器与 CLI；图片型 PPTX；`pptx-editable` 的形状重建、元素回退、字体与文本测量边界。
- [Marp CLI](https://github.com/marp-team/marp-cli)：MIT、Markdown 转换、HTML/PDF/PPTX/图片；`--pptx-editable` 的实验状态、依赖、还原度和备注限制。
- [Presenton](https://github.com/presenton/presenton)：Apache-2.0、桌面/Docker、模板、AI/API、编辑、可编辑 PPTX/PDF。

这些官方能力说明只用于选择工具，不代替对本机版本和实际产物的核验。版本不可用时如实报告，不静默换工具或降低交付要求。
