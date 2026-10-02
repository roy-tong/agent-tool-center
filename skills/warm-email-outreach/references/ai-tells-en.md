# 英文邮件 AI 味词表（外联专用）

与 shuorenhua 的通用英文词表不同，这里按**邮件收件人的识别逻辑**重排：收件人扫一眼就在判断"群发吗？AI 写的吗？"，所以"可移植性"和"表演性礼貌"排在"文笔腔"前面。词表只列代表项，变体按同一模式归类处理。

## 1. 一票否决（任一命中即重写）

### 1.1 无锚点赞美（praise without an anchor）

| 病灶 | 为什么致命 | 替代 |
|---|---|---|
| "I've been following your amazing work" | 换任何收件人都成立=群发实锤 | 引一个具体产出："your retry-semantics comment on #4168" |
| "Your project is truly impressive" | AI 和模板邮件最爱 | 引一个具体数字/文件/决定 |
| "You're doing groundbreaking work in X" | 渲染词+零信息 | 删掉，直接进正事 |
| "I love what you're building" | 每封 AI 冷邮件的第一句 | 同上 |
| "incredible insights in your post" | 无所指的吹捧 | 引帖子里的原话并接一个真问题 |

### 1.2 万能开头（universal openers）

| 病灶 | 替代 |
|---|---|
| "I hope this email finds you well" | 删。第一句直接是钩子 |
| "I hope you're doing well" | 删 |
| "I hope your week is off to a great start" | 删 |
| "My name is X and I am reaching out..." | 自我介绍后置；开场是对方不是你 |
| "I came across your profile/project/article" | 换成你是从哪来的："your comment on {具体处}" |
| "I stumbled upon your repo" | 同上 |
| "I wanted to reach out because..." | 删掉这层宣告，直接说事 |
| "I'm reaching out to..." | 同上 |

### 1.3 元话语自证（meta-disclaimers）

| 病灶 | 为什么致命 |
|---|---|
| "I know you get a lot of emails, so I'll keep this short" | 越声明越像群发；短不需要宣告 |
| "This is not a mass email / not a blast" | 实测教训：写这句的早期邮件全部是批量生成的（真实案例见 before-after.md 第 2 组） |
| "I'll be brief" | 删 |
| "I apologize for the cold outreach" | 道歉把"打扰"变成双重打扰；删掉，用钩子本身抵消陌生感 |
| "Feel free to ignore this" | 给了不回的许可，还占一句 |

### 1.4 空洞 CTA

| 病灶 | 替代 |
|---|---|
| "I'd love to hear your thoughts" | "Would X be an acceptable middle?"——一个能一句话回答的判断题 |
| "Let me know what you think" | 给 2-3 个"好回复长什么样"的具体选项 |
| "Open to a quick chat?" | 首触禁用；先 L1/L2（见 SKILL.md 3.4） |
| "Looking forward to your reply" 作为唯一收尾 | 删或换成具体低请求 |

## 2. 高危项（命中即改）

### 2.1 结构指纹

- **三段排比 / 三条 bullet**：个人邮件不列 bullet。卖点最多一处双元素对比。
- **"Not only X, but also Y"**：AI 的招牌二元拔高，直接说 Y。
- **完美对称**：每段等长、每句等长。制造长短落差，允许两词句（"Worth a look?"）。
- **em dash**：本项目外联门禁明确封禁（AI 指纹）。用句号、逗号或拆句。
- **首字母大写+title case 的营销主题行**（"Transform Your Workflow Today!"）：主题行小写、具体、带上下文。

### 2.2 过度礼貌堆叠

| 病灶 | 替代 |
|---|---|
| "I was wondering if perhaps you might..." | "Would you..." |
| "If it's not too much trouble" | 删 |
| "I completely understand if you're too busy" | 删（对方没说不忙，别替他拒绝） |
| "Whenever convenient / at your earliest convenience" | "when you have a spare hour"（给具体刻度） |

### 2.3 本项目实测封禁句（check_send.py ANTI_TEMPLATE_PHRASES，来源：`projects/AgentMeasure/市场推广/GTM工作区/newoutreach/check_send.py`）

早期波次用滥后成了我们自己的指纹，门禁已封禁，禁止再写：

- "one boundary I can't settle"
- "I'm building"（作开头句式）
- "a quick yes/no"
- "I saw your work"
- "context if useful"
- "either answer would help"
- "I lean A" / "I lean B"（作固定句式）

处理办法不是找同义句替换（换词躲指纹还是指纹），而是把这句承担的功能用**收件人专属的具体内容**重写：比如 "either answer would help" 要传达的"低压力"，用把问题本身改小来传达。

### 2.4 问句失衡

- 恰好 1 个问句（实测最优）；0 个=没有回复入口；3+ 个= "interview mode"，收件人压力大直接弃信。
- 反问句、设问句、客套问句（"How has your quarter been?"）计入且全部属于空洞 CTA，删。

## 3. 密度信号（单个放行，扎堆即改）

- 渲染词：revolutionize / game-changer / cutting-edge / seamless / unleash / supercharge。
- 垫片连用：同时出现 "Thanks so much in advance" + "Looking forward to hearing from you" + "Have a great week"。留一个，删两个。
- 完美语法贯穿全文：真人写作有小碎片句。允许口语缩写（"we're"、"doesn't"）、允许一句以介词短语结尾。
- "I'm thrilled / excited to share"：推销腔，降为直陈。

## 4. 正向参照（人味从哪来）

- 一个带出处的数字："the $30k-since-April line on your case study"。
- 一个文件名/issue 号/向量名：精确到对方可以点开或想象的位置。
- 两词句、小写主题行、一句一段。
- 一层礼貌 + 直接的动作："Would you read X and tell me whether Y?"
- 真实署名：名字 + 一行身份 + 链接，不堆 title。
