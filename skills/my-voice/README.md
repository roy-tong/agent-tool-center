# my-voice

个人默认表达优化 skill，用于 Claude Code / ZCode 等 agent（兼容 [Agent Skills](https://code.claude.com/docs/en/skills) 规范：目录 + SKILL.md + 按需加载的 references）。

管报告、普通 deck、融资 BP 和公开写作的从零创作与常规改写，所有文字共享一条通用底线。

## 通用底线（三去）

- **去机翻**：长定语链拆短、被动改主动、名词化还原动词，清洗翻译腔
- **去 AI 味**：清理空话、机械对比、同构段落与重复结论；有真实信息的对比和原稿有效节奏保留
- **去自造词**：术语判断三问——标准是「目标读者认不认」，不是「字面好不好懂」

## 场景

| 模式 | 要求 | 细则 |
| --- | --- | --- |
| 报告 | 全面完整、叙述简单清晰；结构正当，模板腔不是 | [references/report.md](references/report.md) |
| deck | 每页信息密度高、结合图表、符合演示场景；扫 5 秒讲 30 秒 | [references/deck.md](references/deck.md) |
| 融资 BP / VC pitch | 用市场证据和创始人执行力回答投资人的核心疑问；数字、履历与未知项经得起追问 | [references/deck.md](references/deck.md) + [references/bp-deck.md](references/bp-deck.md) |
| 自媒体 | 有独立判断、故事感、幽默和活人感；事实与经历仍需真实 | [references/social.md](references/social.md) |

当前没有经过用户确认的亲笔文风样本。[已确认偏好与校准方法](references/voice-calibration.md)把王小波式独立思考、故事与幽默，以及半佛仙人、葬AI带来的“活人感”放在中心。其他科技作者的[可迁移技法](references/creator-techniques.md)按选题调用。用户对具体成稿的反馈优先于这份初版画像。

## 安装

```bash
git clone https://github.com/roy-tong/my-voice.git ~/.agents/skills/my-voice
```

克隆到 `~/.agents/skills/`（用户级，所有项目生效）；只想在单个项目用的话克隆到该项目的 `.agents/skills/` 或 `.zcode/skills/`。

## 文件结构

```
my-voice/
├── SKILL.md              # 通用底线 + 模式路由 + 输出合同
└── references/
    ├── report.md         # 报告模式细则
    ├── deck.md           # deck 模式细则（含图表选型）
    ├── bp-deck.md        # 投资人融资 BP：市场、团队、证据、口径
    ├── social.md         # 自媒体写作与平台变形
    ├── voice-calibration.md # 已确认偏好、未知项与校准方式
    └── creator-techniques.md # 参考作者的技法与适用条件
```

## 致谢

风格整合参考了这些公开的 skill 与写作样本：

- [khazix-skills](https://github.com/KKKKhazix/khazix-skills)（数字生命卡兹克的公众号写作 skill）
- [shuorenhua](https://github.com/MrGeDiao/shuorenhua)（中文优先的去 AI 味改写 skill）
- [葬AI](https://funeralai.cc/articles)、[半佛仙人授权文章](https://www.woshipm.com/ai/6351355.html)、[歸藏](https://www.guizang.ai)、[宝玉的分享](https://baoyu.io)、[Simon Willison](https://simonwillison.net/)

## License

[MIT](LICENSE)
