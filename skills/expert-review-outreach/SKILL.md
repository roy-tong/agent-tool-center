---
name: expert-review-outreach
description: 求评式外联（Raju 模式）：以真实身份、具体来历钩子和"三个好反馈的例子"，请目标人物评审自己的仓库/规格/fixture，把对方放在专家位置。用于 AgentMeasure 等开发者工具的邮件冷触达与暖回访；当问句式冷邮件失效、或目标是维护者/活跃贡献者时优先选用。触发词：求评式外联、评审邀请邮件、按 Raju 模式发邮件、expert review outreach、请人评审我们的仓库。
---

# 求评式外联（Raju 模式）

让目标人物给你反馈，而不是你给目标人物推销。收件人被放在专家位置，发件人以
透明的真实身份站在谦逊的建设者位置。这是 2026-09 AgentMeasure 全部外联渠道里
单位转化率最高的互动形态（对照：冷问句式 0 回复 / 26 封；求评互动 Gunjan、
Jaden、David 三人全部转化为规格级贡献）。

## 什么时候用

- 目标是某项目维护者或活跃贡献者，其工作可被具体引用（"I noticed your
  contributions to X"必须能落到真实 PR/issue/comment，写邮件前先找到那个链接）。
- 你有一个可评审的具体物件：仓库、spec 文档、fixture、validator。没有物件就
  不适用本模式。
- 优先于问句式冷邮件的场景：对方层级较高（staff+）、对方维护观测/遥测类项目、
  或对方已经在做相邻领域的东西（互补而非竞争）。
- 不适用：纯使用方、无公开足迹的人、以及竞争对手的维护者。

## 七要素（缺一不发）

解剖自 Raju Dandigam 2026-09 的原信（正文 5 句话，Staff SWE at Navan，全署名）：

1. **具体来历钩子**：引用对方一个真实、可验证的贡献，精确到项目名。不是
   "I saw your work"（那是反模板门禁词），而是"你在 X 的 Y"。
2. **身份透明**：真名 + 职位/公司 + 一个可点开的身份链接（GitHub/LinkedIn/
   个人站）。匿名求评等于索取消费。
3. **一句话定位**：你的物件是什么、给谁用，含一个聪明的补位声明
   （"before or alongside an OTel pipeline"式的不竞争定位）。
4. **具体且低成本的请求**：quick review of the repo。不是 15 分钟通话、不是
   注册、不是 demo。看仓库就是全部成本。
5. **给出"什么算好反馈"的例子**：列出 2-3 个具体产出物
   （"One missing field, confusing behavior, or representative trace
   fixture"）。把模糊的"给我反馈"变成收件人立刻知道怎么回的选项。
6. **利他/专家框架**：请求的是对方的判断力，不是对方的时间表。
7. **5-8 句正文**。没有 feature 列表、没有价格、没有 unsubscribe 脚注、
   没有"hope this finds you well"。

## AgentMeasure 版骨架

正文骨架（槽位必须逐封填实，禁止两封正文相同）：

```
Hi {名},

{来历钩子一句：精确到对方的具体贡献，最好附一处我们能共鸣的细节}

{我们的物件一句话定位 + 与对方工作的互补点：AgentMeasure 是 agent 使用
度量的开放标准，你正在做的 {对方的事} 正是 {我们物件} 要钉死的边界}

Would you be open to a quick read of {具体物件：不是整仓库，优先指到
具体文件/目录} and tell me whether {一个对方有资格回答的判断题}？
{2-3 个具体反馈例子，其中至少一个是我们真的缺、真的想要的，
例如 fixture / 缺字段 / 语义裁决}

{身份：Roy Tong + 一行署名，链接仓库}
```

已验证的物件选项（按请求成本从低到高）：
- conformance/vectors/metric-execution-grain.json（三个重试向量）
- design-rationale/DR-005（两态消费模型，Gunjan 案例证明可转化）
- conformance/evidence/ 下任一 fixture 家族
- TRUST.md 证据分级（Authentication/Corroboration/Independence/Attestation）

## 硬门（在通用反模板门禁之上追加）

发送前逐条检查，任一不过即不发：

- [ ] 来历钩子可验证：能在 2 分钟内向第三方指出对方的那条贡献（PR/issue/
  comment 链接存在）。
- [ ] 署名完整：真名 + 至少一个身份链接。
- [ ] 请求指向具体文件/目录，不是"看看我的仓库"。
- [ ] 给出了 2-3 个"好反馈长什么样"的具体例子。
- [ ] 正文 5-8 句（60-130 词），恰好 1 个问句。
- [ ] 无价格、无 feature 列表、无退订脚注、无 em dash、无反模板门禁词
  （见 市场推广/DeepSeek/newoutreach/check_send.py 的 ANTI_TEMPLATE_PHRASES）。
- [ ] 收件人不在 suppress 名单 / 退信名单 / 8·22 事故名单。
- [ ] 同一收件人 30 天内未收到过任何轨的邮件。

## 发送与跟踪纪律

- 复用现有发送器（事务状态机、回读校验），campaign 注册为
  `expert_review_v1`（anti_template=True）。
- **两级产能模式**（2026-09-17 起，替代旧的每日 ≤10 上限）：
  - **深钩模式**：高价值目标（CEO/CTO/维护者/官方域名地址），
    逐封人工级钩子，每日 ≤ 10 封，间隔 60-150s。质量优先。
  - **矩阵模式**：批量波，素材矩阵生产（6 桶真实审计案例 ×
    钩子/进展/物件/判断题/反馈例子多维变体，body hash 全局去重），
    每日 50-100 封，间隔 30-60s（--fast 档）。矩阵模式的前提：
    全部门禁通过、每封正文唯一、无深钩目标混入。
- **熔断条件**（沿用 8·22 事故复盘规则）：单波退信率 > 5% 立即停发
  复盘；连续 3 封发送失败停发查浏览器；新退信地址实时入 suppress。
- **池子补给**：矩阵模式会以每日 50-100 的速度耗尽池子，挖矿脚本
  （mine_advisory_emails.py / mine_batch_b.py 模式）需同步启动：
  优先从我们已合并修复的 11 个上游仓库的贡献者、audit 报告涉及的
  repo 维护者、以及 OTel/MCP 生态新贡献者挖 V3 验证地址；数字
  handle 型直接弃（退信率 25%+，两次波的教训）。
- 转化口径（沿 traction_discipline，不与人数相加）：
  - reply = 回复（含一句"没空"也算，记 plain）；
  - material = 对方给出具体反馈被采纳进 spec/fixture（记 design-contribution）；
  - artifact = 对方开 PR / 引用我们的 fixture / 在自己项目里接入（最高级）。
- 收到反馈必须在一周内落到仓库并有可回链接，再把链接回给对方——
  闭环本身就是下一次互动（参考：David 的 fixture 从求评到入库 7 天）。

## 范例

原件（Raju Dandigam 2026-09 的来信，仅作内部学习参考，勿对外转载；全文
存于 ~/.agentmeasure/outreach/agent-replies-20260917.jsonl 同轮日志）：

> Hi Roy,
> I noticed your contributions to OpenLIT. I am looking for practical feedback
> from developers who have touched agent observability and OpenTelemetry-oriented
> instrumentation.
> I am building agent-inspect, a local-first TypeScript workbench for inspecting
> agent runs, tool and LLM calls, failures, durations, and redacted evidence
> before or alongside an OTel pipeline.
> Would you be open to a quick review of the GitHub repository and tell me
> whether its local execution-tree model would be useful beside an OpenLIT
> workflow? One missing field, confusing behavior, or representative trace
> fixture would be especially valuable.
> Thanks & Regards / Raju Dandigam / Staff Software Engineer at Navan / {链接}

我们自己方向的同类成功（模式内证）：
- Gunjan Jaswal：被邀请评审 DR-005 草案 → 两轮深度回复 → reframing 进规格
  → 具名贡献 → 第三轮主动补充 orchestration-determined influence。
- Jaden：自跑 conformance validator → 提交两个外部 fixture → CI 采用。
- David Turner：署名互动后主动捐出 inference-boundary fixture
  （aggregation-replay 歧义用例，2026-09 入库）。

三者共同点：请求的是判断，给的是署名与采纳，闭环都落回了仓库。

## 防御视角：别人对我们用这招时怎么识别

这套邮件的来历钩子（"I noticed your contributions to X"）本身就是完美的
模板变量槽位——收到时按五步验对方项目底子，再决定投入多少：

1. **stars/forks/watchers 比例**：自然形态约 fork:star 1:5~1:10 且
   watchers>0；"高 star、零 fork、零 watcher"是非自然特征（我们自己
   买过 stars，教训在案：traction 纪律的 purchased 分层）。
2. **issue 构成**：自提 issue 占大头 = 自驱型早期项目（不是罪，但
   用户基数小）；有多个真人外部 issue = 有人真在用。
3. **代码实质**：宣称的核心功能在文件树里找得到对应实现，还是
   README 驱动开发（查 git tree、抽 2-3 个功能关键词）。
4. **贡献者与时间线**：单人 + bot + 个位数零星贡献者是常态；创建
   不到 3 个月而 star 增长陡峭，外联营销成分概率高。
5. **互补性判断**：对方定位是补位（"before or alongside X"）还是
   竞争。补位才值得回，竞争给礼貌的关门。

2026-09 实测案例：agent-inspect（Raju Dandigam）——真实工程
（752 个 TS 文件、15 贡献者、外部 issue 存在、fork:star≈1:6 健康），
但自提 issue 占 70%、4 个月 603 stars 曲线含外联成分。判定：
及格线以上、思路真、验证少；给反馈、不给背书。回信措辞保持
条件式（"if X renders honestly"），把判断权留给对方的表现。
