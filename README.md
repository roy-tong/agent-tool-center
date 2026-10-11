# 工具中心（agent-tool-center）

第一方 skill、管线和工具产品的唯一存放点。所有 agent 端（ZCode / codex / dsh / 其他）通过稳定路径或符号链接引用这里的资产，不再各自维护副本。

本仓库收录**第一方且未单独建仓**的资产；已有独立仓库的产品和第三方 skill 不在本仓库内（见下表"外部链接"列）。

## 目录

```
├── skills/        skill（三类：第一方实体 / 产品仓库挂载 / 第三方，清单见第 4 节）
└── pipelines/     可执行管线（第一方实体 + 产品仓库挂载，清单见第 4 节）
```

**外部产品仓库**：[bilibili-transcript-pipeline](https://github.com/roy-tong/bilibili-transcript-pipeline) · [deck-scaffold](https://github.com/roy-tong/deck-scaffold) · [deck-humanizer](https://github.com/roy-tong/deck-humanizer) · [user-demand-research (SURE)](https://github.com/roy-tong/user-demand-research) · [iRead](https://github.com/roy-tong/iRead) · [research-to-publish](https://github.com/roy-tong/research-to-publish) · [marketing-ops-automation](https://github.com/roy-tong/marketing-ops-automation)

（已归档留档：[x-ops-automation](https://github.com/roy-tong/x-ops-automation) 已并入 marketing-ops-automation；[my-voice 独立仓](https://github.com/roy-tong/my-voice) 已并入本中心 skills/my-voice）

## 四条产品线

### 1. 研究线 —— SURE 为核心

日常研究主力是 **SURE**（爬数据、做分析、出研究最常用）；媒体转写作证据输入。iRead 已移出研究线，降级为终端应用的可选信源监测输入（全量跑批资源占用大、链路慢、成本高，按需低频启用）。

| 产品 | 模式 | 输入 → 输出 |
|---|---|---|
| **SURE / user-demand-research**（核心，projects/用户需求研究，[roy-tong/user-demand-research](https://github.com/roy-tong/user-demand-research)） | 项目制深度研究 | 研究问题 → 采集→清洗→打标→信号→审计 → 证据分级报告 + BRD/MRD/PRD 整合层 |
| **bilibili-transcript-pipeline**（本中心 pipelines/ 挂载） | 媒体证据转写 | B站视频/本地音视频 → transcript.md（时间戳逐字稿） |

接线契约：
- **bilibili → SURE**：本地访谈录音走 `transcribe` 产出逐字稿，按 SURE `templates/interview-kit/runbook.md` 消化为纪要，`source_family: interview` 入 evidence.jsonl（已接线）。
- **SURE → report-html**：`06-report` 的 md 用 `pipelines/report-html` 合并成单文件 HTML 交付（`build_report_html.py -i <报告目录> -o <项目名>-总览.html`）。
- **SURE → research-to-publish**：证据分级报告作为终端应用的来源快照导入（`ingest case`），进入内容生产。

### 2. 终端应用 —— 内容×运营全链路

一个应用产品覆盖「研究 → 文章 → 公众号/小红书交付 → 账号运营」，主体是 research-to-publish（全链路入口与数据枢纽，生态位总表见其 README「全链路生态位」）：

- **research-to-publish**（主体，[roy-tong/research-to-publish](https://github.com/roy-tong/research-to-publish)）：来源快照 → 稿件 → my-voice 审稿 gate → review → 三平台交付包 + 发布回执（零依赖 CLI + skill）
- 输入端：SURE 证据分级报告（`ingest case`）、bilibili 逐字稿、本地项目文本；iRead 周报作可选信源监测输入（见研究线注记）
- 运营端：**marketing-ops-automation**（[roy-tong/marketing-ops-automation](https://github.com/roy-tong/marketing-ops-automation)）：交付包与文章链接进发布队列，X / Email / Reddit / LinkedIn / GitHub 渠道执行（统一六原语 + 写路径事务管道 + 账本；CLI / MCP / Skill 三形态；X 渠道 vendor 自已归档的 x-ops-automation）
- 发布出口：[roy-tong.github.io](https://github.com/roy-tong/roy-tong.github.io)（博客 + llms.txt 只读 agent 索引）

### 3. 材料线 —— 交付物生产 + 审稿 gate

- **deck-scaffold**：HTML deck 工程脚手架（新 deck 从 `create-deck.sh` 初始化，禁止整目录复制旧项目）
- **pptx-deck-toolkit**：python-pptx 直排（内容契约 + 几何审计器，python-pptx直排谱系 deck 的工程化）
- **deck-humanizer**（skill）：deck/PPT/BP 文案去 AI 味去机翻味
- **report-html**：项目文档 → 单文件 HTML（工作区"一个项目一个 HTML"约定的标准生成器）
- **my-voice（审稿 gate）**：所有对外输出（报告、deck、融资 BP、文章）在 review / 交付前过 my-voice 表达质量底线（去机翻 / 去AI味 / 去自造词）；终端应用的生产流程已内嵌该步骤（r2p README 真实生产段）

### 4. 组件与小工具清单

第一方 skill（本中心 `skills/` 实体，canonical 唯一源）：

| skill | 用途 |
|---|---|
| my-voice | 默认表达 + 对外输出审稿 gate（三去底线，见材料线） |
| warm-email-outreach | 1:1 邮件外联（千人千面、先拉近距离再谈正事） |
| expert-review-outreach | 求评式外联（Raju 模式，请目标人物评审仓库/规格） |
| b2b-account-mapping | B2B 触达前的目标解析与换人协议 |

第一方管线（本中心 `pipelines/` 实体）：

| 管线 | 用途 |
|---|---|
| report-html | 多 md → 单文件 HTML 报告（文档树导航+搜索，纯标准库） |
| pptx-deck-toolkit | python-pptx 直排契约 + 几何审计器 |
| chatgpt-deepseek-workflow | 双模型协作 agent：ChatGPT（网页版，浏览器驱动）出方案与评审，DeepSeek 编码落地，零 API key |
| document-processing | docx 联系表 / contact sheet 生成脚本 |
| ui-automation | macOS 原生键鼠模拟小工具（Swift：click_at / scroll_at） |

挂载副本（产品仓库为上游，本中心只做挂载，更新走仓库发版后重新挂载）：
`skills/`: bilibili-transcript、deck-humanizer、iread、user-demand-research · `pipelines/`: bilibili-transcript-pipeline、deck-scaffold

第三方 skill（不在本仓库分发）：khazix-writer、impeccable、shuorenhua（上游 MrGeDiao）

## 各端接入方式

克隆本仓库到任意固定位置（下称 `$TC`），然后：

| 端 | 接入方式 |
|---|---|
| Claude Code / ZCode 等 | `ln -s $TC/skills/<name> ~/.agents/skills/<name>`（或各端等价 skill 目录） |
| codex | `ln -s $TC/skills/<name> ~/.codex/skills/<name>`；skill 目录内如果引用了绝对路径，克隆后按需改指 |
| dsh / 自建 harness | 直接调用 `$TC/pipelines/<name>` 的稳定路径（各管线自带 README） |

本地实际挂载状态（示例）：ZCode 端 11 个 skill 全部符号链接到本中心；codex 端重复副本已替换为链接。

## 维护纪律

1. skill 和管线只有这里一份实体；任何端不再复制，只挂链接
2. 产品仓库内的 skill（SURE/iRead/bilibili）以仓库为上游，本中心只做挂载；更新走仓库发版后重新挂载/刷新
3. 新工具先落 `pipelines/`，验证稳定后再决定是否独立成 GitHub 仓库
