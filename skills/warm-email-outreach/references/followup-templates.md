# Follow-up 与收口模板

配套 SKILL.md 第 5 节（节奏）使用。所有模板槽位必须逐封填实；示例已脱敏。核心原则：**跟进邮件必须携带新信息，"提醒对方存在一封未回的邮件"不构成新信息**。

## 0. 跟进决策树（先查这张表再选模板）

```
对方回复了
  ├─ 24h 内回，且回应对方话头（不是回到我的 pitch）        → T5
  ├─ 给了反馈/材料                                        → T4 闭环（一周内落仓库回链）
  └─ 拒绝/没空                                           → 记 plain，30 天冷静期，不说服
首触未回（≤7 天）
  └─ 什么都不做。不发 bump。
首触未回（7-14 天）
  └─ 有新钩子（对方新动态/我方新进展与他相关）才发          → T2 新角度首触
     没有新钩子 → 继续沉默
第二次仍未回
  └─ 移出活跃队列。只在出现强新钩子时再评估，否则永不。
LinkedIn 邀请
  ├─ 被接受 → 24h 内发完整信                              → T3
  └─ 7 天未接受 → 不打扰（绝不二次邀请，撤回触发 3 周锁定）
我方出错（误发/空正文/错名字）
  └─ 尽快、简短、不解释基础设施                           → T6
```

冷却规则：同一收件人 30 天内不收到第二封（跨所有轨合并计）。

---

## T1 · 首触（对照用，骨架见 SKILL.md 4.1）

主题：{对方语境的具体事物，小写}

一句话自检：删掉这封信里所有关于"我"的句子，剩下的是否仍然足够让对方想回？不是就还没写好。

## T2 · 新角度再触（7-14 天后，唯一允许的"跟进"）

不发 "following up"。发一封**主题不同、钩子不同、请求更小**的新信，可以不提上一封。

> Subject: {新钩子，与上一封主题无关}
>
> Hi {名},
>
> {新钩子：对方最近的新动态（新帖/新发布/新评论），或我方与他相关的新进展}
>
> {一句话连接：这个新事实与他上封没回的那个话题的关系，不指责没回}
>
> {请求：比上封低一级。上封 L2 这次 L1，上封 L1 这次 L0 纯给予}
>
> {署名}

例（我方新进展角度，纯给予）：
> Subject: that retry ambiguity you'd hit — now settled in spec
>
> Hi {名} — the retry-counting question from a couple weeks back got settled in the spec (attempt count as attribute, backoff latency separated). Dropping the link in case it's useful for {对方项目}, no reply needed.
>
> {署名}

禁止：不写 "I know you're busy"、不写 "just in case you missed this"、不重复上一封正文。

## T3 · LinkedIn 邀请备注 + 接受后完整信

**邀请备注（≤300 字符）**——钩子+一句身份，不含请求：

> Hi {名} — your {案例页/帖子} line "{原话数字}" came up while we mapped how teams verify {对方领域} numbers. I build the open standard for exactly that. Would value a practitioner's read of our one-page draft.

**接受后完整信（24h 内）**——完整骨架见 SKILL.md 4.1，开头一句 "Hi {名}, thanks for connecting." 之后立即进钩子，不做第二层寒暄。

纪律：每日邀请 ≤8；7 天不接受不追；接受后 24h 内发信。

## T4 · 闭环回执（对方给过反馈后，一周内）

这是实测转化率最高的一种"跟进"：把对方的输入落成可见结果，再回去。

> Subject: {对方那个点} — now in the spec
>
> Hi {名},
>
> {对方输入 → 具体改动的 before/after，两三行，可点开}
>
> {链接：改动所在（文件/issue/PR）}
>
> {署名告知：匿名引用了你的观点（"external reviewer, {ecosystem}"），愿意具名随时说}
>
> {可选 L1 请求：one-line comment confirming this captures your point。只回过一轮的人，连这个请求也不发——纯告知即收口}
>
> {署名}

降 CTA 规则：信任每多一轮最多升一级。只回过一轮的人用 L0（纯告知），深谈过两轮以上才请评论/署名。

## T5 · 对话中的回复（24h 内）

原则：回应对方说的，不趁机推销。

- 对方提了观点 → 先接住观点里具体的部分（同意/分歧+理由），再给物件。
- 对方问了问题 → 直接回答，不知道就说不知道（"haven't tested that" 是合法回答）。
- 对方怼了 → 认可对的部分，条件式回应其余（"if X holds, then Y"），把判断权留给对方表现。
- 每封信仍然恰好 1 个问句或 0 个问句（收口信可以无问句）。

## T6 · 事故修复信（误发/空正文/错称呼后，尽快发）

实测文案（449 封空正文事故的道歉信，逐字可用）：

> Subject: Correction: {原主题}
>
> Apologies — my previous email went out without the message body due to a sending error. Resending the intended note below.
>
> {完整正文}

规则：
- 不解释 pipeline/automation/batch/基础设施——"sending error" 一个词够用，多说多错（AI 味+群发实锤）。
- 不假设邮件线程成立（协议层设不了 In-Reply-To 就不假装），主题用 "Correction: {原主题}"。
- 收件人分层：高价值逐封手写道歉；低契合的直接放弃修复（"不打扰本身就是正确决策"）。

## T7 · 求转介绍 / 求引荐（只在对方已表达兴趣后）

> Subject: one intro that would help — {被介绍人的处境}
>
> Hi {名},
>
> {为什么是这个人在这个时刻：他的公开处境与新近发言，不是我们的需求}
>
> If you know them and it feels natural, a three-line intro would help: {一句话我是什么} + {一句话为什么找他}。If not, no worries at all — I'll find another route.
>
> {署名}

规则：给对方现成的转发话术（三行以内）；给"不介绍"的许可且是真心的；介绍请求一次只问一个人。

## T8 · 名单级再触达（给过数字反馈/投票/用过的用户群）

适用于"打过交道但久未联系"的人群（实测 A 轨：合作者体验+star 邀请）：

> Subject: {他当初的那个点}，{N} weeks later
>
> Hi {名},
>
> {他当初的输入/行为} → {现在变成了什么：进了 spec / 被真实数据验证 / 活下来了}
>
> {一个具体结果细节，证明不是客套汇报}
>
> {可选软请求 + 不做许可："if it's been useful, a star helps others find it; if not, I'd rather hear why."}
>
> {署名}

---

## 附：follow-up 邮件的自检三条（在 SKILL.md 六三件套之上追加）

- [ ] 这封信删掉后，对方损失了什么具体信息？答不上来 = 这封信是 bump，不发。
- [ ] 与上一封相比，请求级别没有升高（只可持平或降低）。
- [ ] 主题行与上一封不同（同一个主题反复出现=催促信号）。
