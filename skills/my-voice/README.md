# my-voice

个人默认表达优化 skill，用于 Claude Code / ZCode 等 agent（兼容 [Agent Skills](https://code.claude.com/docs/en/skills) 规范：目录 + SKILL.md + 按需加载的 references）。

管三类常输出物的从零写作与常规改写，所有文字共享一条通用底线。

## 通用底线（三去）

- **去机翻**：长定语链拆短、被动改主动、名词化还原动词，清洗翻译腔
- **去 AI 味**：禁词（说白了/这意味着/赋能/抓手……）、禁结构（二元对比骨架、金句收尾、对仗空转）、防改过头的最小修改哲学
- **去自造词**：术语判断三问——标准是「目标读者认不认」，不是「字面好不好懂」

## 三模式

| 模式 | 要求 | 细则 |
| --- | --- | --- |
| 报告 | 全面完整、叙述简单清晰；结构正当，模板腔不是 | [references/report.md](references/report.md) |
| deck | 每页信息密度高、结合图表、符合演示场景；扫 5 秒讲 30 秒 | [references/deck.md](references/deck.md) |
| 自媒体 | tong 风格：一线动手者视角 + 审计纪律 + 干燥冷幽默 | [references/social.md](references/social.md) |

自媒体模式是本 skill 的核心差异点：不从「像哪个博主」出发，而是从自己的成稿样本提炼签名特征（结论先行、数字挂来源、自曝错误、否定性证据的防御性写法、方法论外化、利益博弈解剖），再把卡兹克、葬AI、半佛仙人、歸藏、宝玉五家的技法作为配料表融入。风格红线沿用 2026-08-31 全站文章审计：结论先行、每个数字挂来源、控制「不是A而是B」句式、控制加粗密度、结尾不回环。

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
    └── social.md         # 自媒体模式（tong 风格 + 五家技法配料表）
```

## 致谢

风格整合参考了这些公开的 skill 与写作样本：

- [khazix-skills](https://github.com/KKKKhazix/khazix-skills)（数字生命卡兹克的公众号写作 skill）
- [shuorenhua](https://github.com/MrGeDiao/shuorenhua)（中文优先的去 AI 味改写 skill）
- [葬AI](https://funeralai.cc/articles)、[半佛仙人文风拆解](https://blog.ax0x.ai/stealing-styles-zh)、[歸藏](https://www.guizang.ai)、[宝玉的分享](https://baoyu.io)

## License

[MIT](LICENSE)
