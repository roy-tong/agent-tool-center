# Before / After 示例（从真实外联邮件改写，已脱敏）

所有 Before 来自 2026-08/09 真实发出的邮件存档（下方逐组标注来源），After 为按本 skill 规则的重写或当时的成功变体。**人名、公司名已脱敏，个别数字为防检索做了同量级改写**。引用原话保留结构。

---

## 第 1 组·冷触达：通用问句 → 可验证钩子 + 一句话裁决

**Before**（真实发出，模板句式自指密集，0 回复波次的样本形态。来源：`projects/AgentMeasure/市场推广/GTM工作区/newoutreach/bodies_t5/`）

> Subject: quick question about your agent tool
>
> Hi {名},
>
> I saw your work on {对方项目} while mapping the agent-tooling ecosystem.
>
> One boundary I can't settle: when your agent retries a tool 3x, do your dashboards show 3 uses or 1 — and does the distinction matter to you?
>
> My current guess is that the honest answer is somewhere counterintuitive — but I can't see enough real usage data to confirm it from the outside.
>
> Context if useful: we are an open spec trying to define comparable agent-usage semantics.
>
> Either answer would help. Thanks either way.

**问题点**
- 开场钩子不可验证："saw your work on X" 换任何项目都成立（换名测试失败）。
- 三句模板句式自指："One boundary I can't settle" / "Context if useful" / "Either answer would help"——后来自家门禁封禁的正是这三句（check_send.py）。
- 请求没有判断题收口：对方不知道回什么才算回答了。
- 同批次的 26 封问句式冷邮件实测 0 回复（来源：`市场推广/求评式外联-skill-20260917.md`）。

**After**（同 campaign 后期的真实变体，来源：`市场推广/邮件营销-20260910/body_ER3_*`，脱敏）

> Subject: whole-request spans in {对方框架} — one verdict wanted
>
> Hi {名},
>
> your repo's instrumentation wraps the whole logical request in one span, which is exactly where the audit's most common failure class lives. I maintain the open measurement standard that work belongs to, and one judgment from where you sit would sharpen it.
>
> Would you be open to a quick read of conformance/vectors/metric-execution-grain.json in the repo below (the three-attempt vector) and one verdict: would attempt count plus separated backoff latency as attributes be an acceptable middle? If none of it survives your reading, that verdict also helps, as long as it names the line that broke.
>
> {真名}
> {一行身份}
> {链接}

**改了什么**
- 钩子可验证：对方 repo 的具体行为（whole logical request in one span），换人即不成立。
- 请求变成"一个文件 + 一个裁决题"，且给了"否决也算回复"的出口——把回复成本压到最低。
- 模板句全部消失：功能由具体内容承担（低压力不再靠 "either answer would help" 声明，靠把问题改小）。
- 恰好 1 个问句。

---

## 第 2 组·冷触达：元话语自证 + 高成本 CTA → 数字钩子 + 零成本给予

**Before**（真实发出。来源：`GTM工作区/newoutreach/b_generic_mcp.txt` 与 `b_cliff.txt`，合并同类）

> Hi,
>
> I found your work through the MCP server ecosystem, so this is a targeted note rather than a blast.
>
> I run {项目}, an open measurement standard for how AI agents discover, choose, and use capabilities. The core split: 1 intent, 2 provider attempts = 1 operation, 2 attempts.
>
> We are looking for 3 providers for short external measurement runs: fully local, no agent-side install. Best outcome is a concrete counterexample from real traffic.
>
> Interested? / Worth 15 minutes for you?
>
> {名}

**问题点**
- "this is a targeted note rather than a blast"：元话语自证，一票否决项。以及开场没有任何对方专属内容（"found your work through the ecosystem"=没找到具体的人）。
- 自我定位占了正文一半，先推销后请求，结构倒置。
- "Interested?" 空洞 CTA；"Worth 15 minutes?" 首触上高成本 CTA。
- 无署名链接，身份不可核。

**After**（案例客户触达的真实写法。来源：`发现冲刺-20260919/触达批次1-20260920.md`，人名公司脱敏、数字同量级改写）

> Subject: your {厂商} case study number — ever checked it against the bill?
>
> Hi {名} — your {厂商} case study quotes "$40k saved since March" on {产品}. We build the evidence-based way to check the number behind that claim: a free tool that reads your {厂商} export locally (nothing leaves your machine) and produces a two-line statement — what their rules bill vs. what your customers actually confirmed.
>
> Even (especially) happy customers use it before renewal: it turns "we trust the number" into "we verified the number." If you'd like, send a sanitized export or run it locally — 48h turnaround, free, no sales call.
>
> {真名}, {项目}. {链接}

**改了什么**
- 钩子换成对方案例页的公开数字（硬钩子，2 分钟可验证）。
- 删掉"not a blast"，用具体数字本身证明这封信是定向的。
- CTA 从"15 分钟通话"降到"跑一个免费本地工具"，且主动声明"no sales call"把推销预期摘掉。
- 收件人成本归零：发个脱敏导出，或本地自己跑。

---

## 第 3 组·暖回访："还记得我吗"催促 → 带收据回来

**Before**（典型 bump 形态，对照用组合样本——真实档案中此类从未被采用，因为纪律禁止）

> Subject: Re: {原主题}
>
> Hi {名},
>
> Just following up on my previous email — I know things get busy. Did you have a chance to look at the spec draft I sent? I'd still love to get your thoughts when you have a moment.
>
> Thanks in advance!

**问题点**
- 零新信息：这封信存在的唯一理由是催。对方不回第一封的理由（没价值/没空/没想好）一个都没被回应。
- "Just following up" + "Did you have a chance" + "I'd still love your thoughts"：三个空洞 CTA 叠加。
- 给对方的关系记账：只索取，没兑现。暖回访的前提是上一次互动我们给过什么或产出过什么。

**After**（真实发出的暖回访。来源：`邮件营销-20260910/body_hello_at_gunjanjaswal.me.txt` 与 `newoutreach/replies3/david_r1_2026-08-25.md`，脱敏）

> Subject: your reframing, six weeks of traces later
>
> Hi {名},
>
> Your reframing of consumption — availability as a context fact and influence as a behavioral one — has been in the spec for a few weeks now, credited to you by name. It survived contact with real traces better than I expected: in one demo corpus, twelve attempts resolved to zero defensible influence claims, which is exactly the fail-closed behavior the split predicts.
>
> Two small things. Has anything in your own work since contradicted the split? And if the spec has been useful to you, a star on the repo helps other people find it. If it hasn't, no action needed and I would rather hear why.
>
> {真名}

**改了什么**
- 先给收据：对方的输入进了哪里、起了什么作用、被真实数据验证的结果——全部可点开。
- 请求降到 L0/L1："有没有被推翻"是一句裁决题；star 是可选给予且给了明确的不做许可（"no action needed"）。
- 把"催"变成"汇报+一个问题"，这封信本身有独立价值，不再是第一封的回声。

---

## 第 4 组·商务合作：AI 腔推销 → 问信息不问会面

**Before**（AI 腔商务推销的组合样本，汇集真实审稿中反复出现的病灶）

> Subject: Strategic Partnership Opportunity with {项目}
>
> 尊敬的 {名} 您好，
>
> 我是 {公司} 的 {名}，很冒昧打扰您。我一直密切关注您在 {领域} 方面的杰出工作，深受启发。
>
> 我们正在打造一个革命性的开源度量标准，不仅填补了行业空白，更重新定义了 agent 用量的度量方式。我相信双方的合作将实现共赢：
> - 赋能您的客户获得透明的计费体验
> - 共建行业标准生态
> - 打开增量市场机会
>
> 不知您是否有兴趣进一步了解？期待您的回复，顺祝商祺！

**问题点**
- 中文 A 级全中：万能开头（冒昧打扰）、无锚点赞美（杰出工作深受启发）、空洞 CTA（有兴趣进一步了解）。
- "不仅...更..."二元拔高 + 三条 bullet + 黑话（赋能/共建生态）。
- 先推销后无请求：整封信没有一件对方可以具体做的事，也没有一个问题。
- 署名墙式收尾。

**After**（顾问触达的真实写法，来源：`发现冲刺-20260919/发现冲刺工具包.md` C1 模板，脱敏）

> Subject: how are your clients handling AI per-resolution bills?
>
> Hi {名} — I read your {文章/帖子} on {具体主题}. I maintain an open-source project that audits AI usage-metering (110+ tools audited, 21 fixes merged upstream). We've now turned to the billing side: per-resolution invoices where "resolved" is self-attested by the vendor's AI.
>
> One question, from your multi-client seat: how often do your clients dispute these bills, and what does the resolution process look like today? (We're finding most vendors publish no dispute process at all.)
>
> If it's useful: we have a free local tool that turns a {厂商} export into an evidence-based two-line statement clients can take into renewal talks. No charge, no data leaves their machine.
>
> {真名}, {项目}. {链接}

**改了什么**
- 钩子锚定对方的公开发言（具体文章+主题）。
- 身份一句话带可核数字（21 fixes merged upstream），不推销定位语。
- 唯一请求是**信息**：一个只有坐在对方位置（multi-client seat）才答得了的问题——这是商务邮件里把对方放在专家位置的做法。
- 给予放最后且无条件（free / local / no charge），不构成交换压力。

---

## 四组的共同规律

1. Before 的第一句都在说**发件人**（我是谁/我为什么写信/我看了你的"作品"）；After 的第一句都在说**收件人**（你的数字/你的输入/你的发言）。
2. Before 的 CTA 都空或重（"感兴趣吗/聊聊吗/15 分钟"）；After 的 CTA 都具体且便宜（一个裁决题/一个免费工具/一条信息）。
3. Before 靠声明建立信任（not a blast / 深受启发）；After 靠可验证事实建立信任（案例页数字/已合并的修复/落进 spec 的改动）。
4. 每组 After 都通过换名测试：换掉收件人，第一句就崩。
