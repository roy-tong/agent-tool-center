# pptx-deck-toolkit

python-pptx **直排 deck**（代码即内容源）的共享工具：内容模块契约 + 几何审计器。

从两个项目谱系里抽出来，不复制项目文件、不绑定任何一家：

- **该项目 v20**（`projects/某融资deck项目/工具/`：`deck_v20_content.py` + `build_deck_v20.py` + `audit_deck_v20.py` + `build_deck_v20_html.py`）
- **高尔夫**（`projects/高尔夫智能设备调研/scripts/`：`deck_content.py` + `build_deck_pptx.py`，docstring 自述源自脑机接口 deck 版式体系）

## 为什么要有"代码即内容源 + 几何审计"

直排 deck（python-pptx 逐形状绝对定位，不用 PowerPoint 手排版）的失败模式都是**几何级**的：

- 文本折行比预估多一行，溢出文本框压到下方元素；
- 卡片/胶囊的坐标算错，文本压在别人的卡片上（v20 审计注释里点名的"P07/P15 那类致命错位"）;
- 内容底边侵入页脚带、元素出安全边距；
- 字号随手写，同一角色两个页面两种大小。

这些问题在代码 review 里看不出来——`y=4.50, h=1.55` 是否装得下三行 13pt 文本，人眼算不了。渲染成 pptx 再肉眼翻页又太晚、且靠不住（PowerPoint 的 normAutofit 在不同查看器里行为还不一致）。所以这套模式的正解是两道机器检查：

1. **内容层（build 前）**：content 模块过一个契约校验——字段齐不齐、块的 y+h 压没压页脚、同页块重不重叠、有没有没替换的 `【待填】`/`{N}`。
2. **几何层（build 后）**：对生成的 pptx 做审计——用统一的文本宽度估算反推"需要的文本高度"，比对文本框/卡片/页脚带/画布的相对几何。

本工具包把这两道检查从两个项目里抽成共享代码。**只审计、不渲染**；渲染仍归各家 build 脚本（版式是项目资产，不通用化）。

## 文件

| 文件 | 作用 |
|---|---|
| `deck_contract.py` | 内容契约规范化：`DeckContract`（palette/geometry/type_scale/font/footer/slides）+ `from_legacy()` 加载项目甲/高尔夫 content 模块 + `validate()` 内容层校验。纯标准库。 |
| `geometry.py` | 统一 `text_w_pt()` 文本宽度估算（三家实现对比结论见模块 docstring）、`fit_scale` 收缩阶梯、`paras_need_h`、矩形交叠/包含/面积比判据。纯标准库。 |
| `audit_deck.py` | 审计 CLI（依赖 python-pptx）。pptx 模式跑 C1–C10 几何检查；`--content` 模式跑契约校验。 |
| `.venv/` | 本地虚拟环境（唯一依赖 python-pptx），见 `.gitignore`。 |

## 用法

```bash
cd codex/tools/pptx-deck-toolkit
python3 -m venv .venv
.venv/bin/pip install python-pptx        # 唯一依赖

# pptx 几何审计（默认版式参数 = 该项目 v20：13.3333x7.5 / 边距 0.62 / 页脚带 7.00）
.venv/bin/python audit_deck.py ../../projects/某融资deck项目/AgenticCommerce融资BP_Deck_v20.pptx

# 高尔夫系 deck 覆盖版式参数（px 标尺 1280x720：64px 边距，662px 页脚分隔线）
.venv/bin/python audit_deck.py deck.pptx --margin 0.667 --footer-y 6.90

# 内容契约校验（不打开 pptx；自动识别项目 DECK / 高尔夫 SLIDES 形状）
.venv/bin/python audit_deck.py --content ../../projects/某融资deck项目/工具/deck_v20_content.py
.venv/bin/python audit_deck.py --content ../../projects/高尔夫智能设备调研/scripts/deck_content.py

# 只看契约归一结果
python3 deck_contract.py <content_module.py>     # 无需 venv

# 输出 JSON / 严格模式（WARN 也算失败）
.venv/bin/python audit_deck.py deck.pptx --json issues.json --strict
```

退出码：有 ERROR → 1；`--strict` 时 WARN/INFO 也计入。

### 检查项（pptx 模式）

| 代码 | 检查 | 来源 |
|---|---|---|
| C1 off-canvas | 画布外（深色页 Oval 装饰豁免；`--allow-bleed` 降级） | 高尔夫 qa |
| C2 margin | 横向越出安全边距 | 该项目 v20 |
| C3 footer | 压到页脚带 | 该项目 v20 |
| C4 overflow | 文本超出自身文本框（统一 text_w_pt 反推需要高度，行距按 spcPts/spcPct 反读） | 该项目 v20 |
| C5 escape-card | 文本跑出所属卡片（左上角认主、取最小容器） | 该项目 v20 |
| C6 foreign-card | 文本压到"别人的"卡片 | 该项目 v20 |
| C7 card-overlap | 卡片之间重叠（斑马纹背景色、合法嵌套豁免） | 该项目 v20 |
| C8 text-overlap | 文本框两两重叠（交叠>0.06in 双向且面积>15% 小框，默认 WARN） | 高尔夫 qa |
| C9 bottom-gap | 内容底边距页脚线不足 0.18in | 该项目 v20 |
| C10 font | 页脚带字号统一 / 最小字号下限 / 孤立字号 / 字体混用 | 本工具包新增 |

"真问题 vs 刻意设计"的豁免规则继承该项目 v20：页脚带内形状不参与多数检查、深色页装饰圆豁免、全宽浅色斑马纹不算卡片。高尔夫版式的刻意做法（文本压在色带上）由 C5/C6 的"认主"逻辑天然放行。

## 版本管理：用 git，禁止复制 build_deck_vN.py

该项目的现状就是反例：`工具/` 下 **build×20 + audit×19 + content×19 + html×20 ≈ 78 个版本文件**，每版内容差异其实很小，但目录已经不可读，且 text_w_pt 这类基础函数在多个副本里重复。已知损失：任何一处修 bug 都要人肉判断"要不要同步其他副本"，忘了就漂移。

正确做法（本工具包自身的约定，也推荐给 deck 项目）：

```bash
git init
git add deck_contract.py geometry.py audit_deck.py README.md .gitignore
git commit -m "toolkit: 内容契约 + 几何审计器（该项目 v20 / 高尔夫谱系抽取）"
```

之后：

- **内容改动** → 改 content 模块（如 `deck_content.py`，不带版本号后缀），commit message 写清改了哪几页；
- **版式改动** → 改 build 脚本（一个 `build_deck.py` 就够），commit；
- **发版** → `git tag v20` / `git tag golf-v4`，产物文件名可以带版本，**代码不带**；
- **审计进流程** → build 完自动跑 `audit_deck.py`，非零退出码就挡下（pre-commit 或 CI 一行脚本）;
- 回溯用 `git log`/`git diff v19 v20 -- deck_content.py`，而不是肉眼 diff 两个 700 行的副本。

本目录当前没有 git 仓库（按任务约定未执行任何 git 操作）；上面的 `.gitignore` 已备好，`git init` 后即可直接用。

## 来源谱系

### 该项目 v20 贡献了什么

`projects/某融资deck项目/工具/`（只看 v20 这套，v2–v19 即将删除）：

- **内容契约的基准形状**：`DECK`（cover/content/closing 三种页 kind + blocks 列表，block 带 type/x/y/w/h 绝对坐标）+ `TOKENS` 色板（深浅双主题 16 role）+ `GEO` 几何常量（英寸）+ `TYPE` 字号阶梯（pt）+ `FONT` + `FOOTER_LEFT`。`deck_contract.py` 的字段设计与之逐一对齐。
- **18 种块渲染器**的必填字段表（bar/caption/chips/chain_rows/stats/cards/rows/placeholder_rows/twocol/side_panel/chain/timeline/flywheel/phase_panel/table/layers/phones/roles）。
- **文本度量三件套**：`text_w_pt` / `n_lines` / `fit_scale`（0.64–1.0 十档收缩阶梯），以及两条关键经验——行距下限 1.25em（否则 g/y/p 下伸部被切）、行距必须用绝对值 spcPts（spcPct 在 CJK 字体下实际行高多约 35%）。
- **审计检查项主干**：C2–C7、C9 及"页脚带/装饰圆/斑马纹"豁免逻辑。
- HTML 预览器与 PPTX 渲染器共用同一 content 模块、同一套 text_w_pt（双渲染目标一致性的范本）。

### 高尔夫贡献了什么

`projects/高尔夫智能设备调研/scripts/`（自述源自脑机接口 deck 版式体系，那是更早的上游）：

- **四原语 + take 的页模型**：columns/rows/table/metrics（+duo/barlist），每页 `section 眉标 → 结论标题 → 论证副题 → 一个原语 → take 结论条`，来源进 `notes` 讲者备注。这套"一页一原语"比项目的 18 种块更收敛，适合调研型 deck。
- **px 标尺**：1280×720px（px/96=英寸，px*0.75=pt），GEO 常数隐含在 build 里（64px 边距 / 1152px 内容宽 / 662px 页脚线）。
- **bbox 级 QA 判据**：画布外（±0.05in 容差）+ 两两重叠的面积比阈值（交叠面积 >15% 小框才算真重叠）——吸收进 C1/C8。
- 高尔夫**没有**文本宽度估算（见下节），它的策略是"预留大框 + take 条固定高度"，溢出靠肉眼。

### text_w_pt 三处实现的差异结论

核对结果（2026-10）：

1. 项目 `build_deck_v20.py::text_w_pt` 与 `build_deck_v20_html.py::text_w_pt` **逐字节相同**（同样的 1.0/0.28/0.9/0.55 系数，注释自称"与 PPTX 渲染器一致"）；
2. 项目 `audit_deck_v20.py::tw` **逻辑相同**（同系数，缩写名，`size*1.0` 写作 `size`）；
3. 高尔夫 `build_deck_pptx.py` **没有文本宽度估算函数**——任务前提里"高尔夫 build 重复实现了 text_w_pt"不成立，它只有 bbox 级 qa()。

即：三处重复全部在该项目 v20 家族内部（pptx build / html build / audit），系数无漂移，但重复本身是漂移风险（改任何一处都要记得同步另外两处）。统一版以 build（pptx）那份为底——它是唯一参与真实排版决策的——系数不变，补了一个项目原集合遗漏的 `←`（flywheel 块在用），差异全部写在 `geometry.py` 的模块 docstring 里。

### artifact-tool (.mjs) 谱系为何暂未收入

`projects/项目乙/scripts/build_osuga_*.mjs` 走的是另一条路线：`@oai/artifact-tool`（Node ESM，装在 `~/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/` 的 codex 运行时缓存里），px 坐标 + `autoFit: shrinkText` 由库/渲染端处理，配套 artifact-session（host-daemon / MCP）做渲染后的 probe/inspect 回路（渲染出图再检查，视觉级验证）。

暂不收入的原因（现状记录，非永久决定）：

- **运行时绑定**：依赖 codex 运行时缓存路径，不是项目内可声明的依赖，搬进本工具包会破坏"仅 python-pptx 一个依赖"的可移植性；
- **验证层次不同**：artifact-tool 的 probe/inspect 是渲染级（出图看效果），本工具包是静态几何级（读 OOXML 算坐标）。静态层便宜、确定、可进 CI；渲染层贵但在"字体真实度量"上更准——两者是互补而非替代;
- **接口未冻结**：`.mjs` 侧还在随 codex 运行时演进，没有稳定 API 可供抽取。

若未来要做"真实字体度量"的文本宽度（替代 0.55em 估算），合理路径是在 `geometry.text_w_pt` 后面接一个可选的字体后端，而不是引入整套 Node 渲染回路。

## 实测记录（2026-10-02）

**该项目 v20 pptx**（`AgenticCommerce融资BP_Deck_v20.pptx`，24 页，默认版式参数）：

- 几何检查 0 ERROR——与项目自带 audit_deck_v20 的结论一致（定稿版已审计干净）；
- C10 字号一致性：WARN `font-min`——deck 里有 2 个 run 被 fit_scale 收缩到 8.8pt（11.0×0.8），低于 9pt 可读下限；INFO `font-rare`——40/32pt（封面/封底主标题）等孤立字号，属预期设计。

**高尔夫 pptx**（`06-report/deck/商业计划书-deck.pptx`，24 页，`--margin 0.667 --footer-y 6.90`）：

- 44 条（ERROR 20 / WARN 23 / INFO 1）。满幅背景矩形按几何规则豁免后，剩余 ERROR 全部是**高尔夫自家 qa() 结构上看不到的文本级溢出**：take 结论条（26px 字、46px 框、内容两行）在 P02/P06/P11/P14/P15 等页需 0.60in 框仅 0.48in；P10 四栏标题换行后需 0.72in 框仅 0.58in；P13「做/不做」栏正文需 3.24in 框仅 2.58in（估算偏保守，但 ≥0.6in 的信号值得回看渲染效果）；
- WARN `font-footer`：页脚带两种字号（文案 10.5pt / 页码 12.8pt）——高尔夫的刻意设计，属"知道了可以豁免"的一类；
- 这组结果正是"高尔夫没有 text_w_pt"的直接代价：bbox 级 QA 对文本折行无感。

**内容契约**：该项目 v20 content 模块校验通过（仅 1 条 INFO：封面 `foot` 含 `{N}` 页数占位符，build 期替换，属预期）；高尔夫 content 模块校验 0 条。

## 设计边界

- 只读审计，不修改任何 pptx / content 源文件；
- 文本宽度是估算（CJK 1em / 拉丁 0.55em / 空格 0.28em / 宽标点 0.9em），对 Hiragino Sans GB 保守（宁可多折行）；要精确值需渲染级方案，见上节；
- 契约校验是宽松式的：未知块类型/缺坐标只 WARN（两家谱系合法形状太多），缺必填字段才 ERROR。
