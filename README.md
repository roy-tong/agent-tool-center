# 工具中心（agent-tool-center）

第一方 skill、管线和工具产品的唯一存放点。所有 agent 端（ZCode / codex / dsh / 其他）通过稳定路径或符号链接引用这里的资产，不再各自维护副本。

本仓库收录**第一方且未单独建仓**的资产；已有独立仓库的产品和第三方 skill 不在本仓库内（见下表"外部链接"列）。

## 目录

```
├── skills/        第一方 skill（canonical 唯一源）
│   ├── my-voice                   # 默认表达 skill：报告/deck/自媒体三模式 + 三去底线
│   ├── warm-email-outreach        # 邮件外联（千人千面/防AI识别/先拉近距离再谈正事）
│   ├── expert-review-outreach     # 求评式外联（Raju 模式）
│   └── b2b-account-mapping        # B2B 触达前的目标解析与换人协议
│       # 独立仓库：deck-humanizer（PPT/deck 去AI味）、shuorenhua（上游 MrGeDiao）
│       # 第三方（不在本仓库）：khazix-writer、impeccable
└── pipelines/     可执行管线产品
    ├── report-html                # 多 md → 单文件 HTML 报告（文档树导航+搜索，纯标准库）
    ├── pptx-deck-toolkit          # python-pptx 直排契约 + 几何审计器
    └── chatgpt-deepseek-workflow / document-processing / ui-automation
        # 独立仓库：bilibili-transcript-pipeline（B站+本地音视频转逐字稿 v0.3.0）、
        #          deck-scaffold（Vite 系 HTML deck 脚手架）
```

**外部产品仓库**：[bilibili-transcript-pipeline](https://github.com/roy-tong/bilibili-transcript-pipeline) · [deck-scaffold](https://github.com/roy-tong/deck-scaffold) · [deck-humanizer](https://github.com/roy-tong/deck-humanizer) · [user-demand-research (SURE)](https://github.com/roy-tong/user-demand-research) · [iRead](https://github.com/roy-tong/iRead) · [x-ops-automation](https://github.com/roy-tong/x-ops-automation)

## 三条产品线

### 1. 研究线 —— 三个产品，一份契约

| 产品 | 模式 | 输入 → 输出 |
|---|---|---|
| **iRead**（projects/iRead，[roy-tong/iRead](https://github.com/roy-tong/iRead)） | 持续订阅追踪 | 领域 → 信源发现/评分 → 日报/周报/月报 |
| **SURE / user-demand-research**（projects/用户需求研究，[roy-tong/user-demand-research](https://github.com/roy-tong/user-demand-research)） | 项目制深度研究 | 研究问题 → 采集→清洗→打标→信号→审计 → 证据分级报告 + BRD/MRD/PRD 整合层 |
| **bilibili-transcript-pipeline**（本中心 pipelines/） | 媒体证据转写 | B站视频/本地音视频 → transcript.md（时间戳逐字稿） |

接线契约：
- **bilibili → SURE**：本地访谈录音走 `transcribe` 产出逐字稿，按 SURE `templates/interview-kit/runbook.md` 消化为"结论+时间戳证据"纪要，`source_family: interview` 入 evidence.jsonl（已接线）。
- **iRead → SURE**：iRead 的信源清单与周报可作为 SURE `01-sources` 的输入——iRead 批准过的信源（带评分）直接登记为 sources，周报中的新事件线索进候选证据池。
- **SURE → report-html**：`06-report` 的 md 用 `pipelines/report-html` 合并成单文件 HTML 交付（`build_report_html.py -i <报告目录> -o <项目名>-总览.html`）。

### 2. 材料线（对外交付物生产）

- **deck-scaffold**：HTML deck 工程脚手架（新 deck 从 `create-deck.sh` 初始化，禁止整目录复制旧项目）
- **pptx-deck-toolkit**：python-pptx 直排（内容契约 + 几何审计器，python-pptx直排谱系 deck 的工程化）
- **deck-humanizer**（skill）：deck/PPT/BP 文案去 AI 味去机翻味
- **report-html**：项目文档 → 单文件 HTML（工作区"一个项目一个 HTML"约定的标准生成器）

### 3. 运营线

- **x-ops-automation**（projects/AgentMeasure/代码仓库/，[roy-tong/x-ops-automation](https://github.com/roy-tong/x-ops-automation)）：X 运营（CDP 接管真实 Chrome）
- **warm-email-outreach / expert-review-outreach**（skill）：邮件外联

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
