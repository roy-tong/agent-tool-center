# 「ChatGPT 出方案 → DeepSeek 落地 → ChatGPT 复审」标准工作流

一套可复用的双模型协作 agent：**ChatGPT（网页版）负责出方案与评审，DeepSeek 负责编码落地**。
方案和评审由浏览器 agent 直接驱动你已登录的 Chrome 中的 chatgpt.com 完成，无需任何 API key 或凭据。

## 工作流总览

```
┌─────────────┐   阶段1    ┌──────────────────┐   阶段2    ┌──────────────┐
│   任务描述   │ ────────▶ │  ChatGPT 出方案    │ ────────▶ │ DeepSeek 落地 │
└─────────────┘   plan.md  │  (chatgpt_agent) │            │  (编码 agent) │
                           └──────────────────┘            └──────┬───────┘
                           ┌──────────────────┐                  │ output/
       阶段3               │  ChatGPT 复审     │ ◀────────────────┘
       review.md ◀──────── │  (chatgpt_agent) │   实现摘要
                           └──────────────────┘
```

| 阶段 | 角色 | 执行者 | 产物 |
| --- | --- | --- | --- |
| 1 出方案 | ChatGPT | `chatgpt_agent.py plan` | `tasks/<id>/plan.md` |
| 2 落地 | DeepSeek | DeepSeek 编码 agent（读 plan.md 写代码） | `tasks/<id>/output/*` |
| 3 复审 | ChatGPT | `chatgpt_agent.py review` | `tasks/<id>/review.md` |

## 目录结构

```
chatgpt-deepseek-workflow/
├── chatgpt_agent.py     # 浏览器 agent：驱动 chatgpt.com（plan / review / ask / check）
├── run_workflow.sh      # 一键编排：阶段1 → 提示阶段2 → --review 触发阶段3
├── tasks/<task-id>/     # 每个任务一个目录：plan.md / output/ / review.md
├── logs/                # 运行日志与截图
└── README.md
```

## 前置条件（一次性）

1. Chrome 带远程调试端口启动（推荐用 `launch_x.command` 同款方式，或直接运行：
   `open -a "Google Chrome" --args --remote-debugging-port=9222` —— 需先完全退出 Chrome）
2. 在 Chrome 中登录 chatgpt.com（人工登录一次即可，agent 复用该登录态，不存任何凭据）
3. `pip install playwright`（本机已装）

## 使用

```bash
cd chatgpt-deepseek-workflow

# 0) 检查登录态
python3 chatgpt_agent.py check

# 1) 起一个新任务：阶段1（ChatGPT 出方案）+ 阶段2 交接提示
./run_workflow.sh my-task "用 Python 写一个 CLI 工具：统计目录内各扩展名的文件数与总大小"

# 2) 阶段2：DeepSeek 编码 agent 读取 tasks/my-task/plan.md，
#    按方案实现并写入 tasks/my-task/output/（本会话即扮演该角色）

# 3) 阶段3：ChatGPT 复审
./run_workflow.sh my-task "..." --review
```

### chatgpt_agent.py 子命令

| 命令 | 说明 |
| --- | --- |
| `check` | 检查 chatgpt.com 登录态 |
| `plan --task "…" --out plan.md` | 新开对话，让 ChatGPT 输出实现方案（存为 Markdown） |
| `review --task "…" --file 摘要.md --out review.md` | 把实现摘要发给 ChatGPT 复审 |
| `ask --prompt "…" --out reply.md` | 通用一次性对话 |
| `--gpt <id>` | 指定自定义 GPT（如 `g-p-6a29f6ee…` 中的 id） |
| `--keep` | 完成后保留标签页供人工查看（默认用完即关，不污染你的浏览器） |

## 设计要点

- **零凭据**：只通过 CDP 驱动你已登录的 Chrome，不保存密码/Cookie/token。
- **不污染会话**：每次 plan/review 都新开一个独立标签页，完成后自动关闭。
- **Markdown 保真**：提示词要求 ChatGPT 把方案/评审整篇放在单个 ```markdown 代码块中，
  提取代码块内容即得到干净的 Markdown，可原样交给 DeepSeek 落地。
- **可审计**：每步日志输出，方案/报告/元数据（含任务原文、生成时间、对话 URL）全部落盘。
- **防呆**：发送失败自动回车兜底；回复为空自动重试；超时可调（`--timeout`）。

## 阶段2 协议（DeepSeek 落地规范）

DeepSeek 编码 agent 收到任务后按以下协议执行：

1. 通读 `plan.md`，不自行发挥偏离方案；如有必要偏离，在实现说明中标注理由。
2. 按方案"实现步骤"逐文件落地到 `tasks/<id>/output/`。
3. 对照方案"验收标准"逐条自测，把结果写入 `tasks/<id>/implementation_summary.md`。
4. 交给 ChatGPT 复审；若 `review.md` 有修改建议，修复后重跑复审，直到无 ❌ 项。

## 阶段3 协议（复审结果核验——重要）

ChatGPT 评审意见**必须先核验再执行**，不要无脑照单全收：

1. 评审引用的"问题代码"若与产物不符（引用内容在产物中不存在），标记为**误报**，
   不修改产物；误报连续出现时，在任务目录写 `VERDICT.md` 记录核验过程与裁决。
2. 确认真实问题后，按 P0 → P1 → P2 顺序修复；修复后重跑 `--review`。
3. 每次核验的机械检查手段（示例）：
   - 徽章/链接：正则匹配标准格式 `[![alt](img)](url)`、括号配对平衡、
     检查评审声称的损坏模式是否真的出现。
   - 代码：单元测试、CLI 实跑、浏览器实测（前端任务）。
   - 文档：占位符清单与正文使用是否一致。
4. 实测样例教训（2026-08-16 记录）：
   - sample2 连续两轮评审误报"徽章 Markdown 语法损坏"（引用了不存在的损坏版本），
     机械核验 4/4 徽章格式正确、括号平衡、损坏模式 0 次出现 → 判定误报，未修改产物。
   - sample1 第一轮评审正确抓到"实现摘要缺源码"的真实 bug（摘要生成器跳过子目录文件），
     修复后第二轮评审通过 —— 证明该核验协议下评审仍有高价值。

## 验收标准（工作流本身）

- [x] `check` 能确认登录态
- [x] `plan` 端到端：新对话 → 发送 → 等待 → 提取 Markdown 方案落盘
- [x] `review` 端到端：实现摘要 → 评审报告落盘
- [x] 样例任务全部跑通（见 `tasks/` 下各样例目录）
