# my-voice

个人默认表达优化 skill，用于 Claude Code / ZCode 等 agent（兼容 [Agent Skills](https://code.claude.com/docs/en/skills) 规范：目录 + SKILL.md + 按需加载的 references）。

管报告、普通 deck（含管理层汇报）、业务 BP、融资 BP 和公开写作的从零创作与常规改写。通用底线、场景路由和输出合同以 [SKILL.md](SKILL.md) 为唯一正本，本 README 只做安装与结构导航。

## 场景与细则

| 场景 | 主细则 | 继承 |
| --- | --- | --- |
| 报告 | [references/report.md](references/report.md) | — |
| deck（普通 + 管理层 / 经营汇报） | [references/deck.md](references/deck.md) | — |
| 业务型 BP / 多产品族方案 | [references/bp-business.md](references/bp-business.md) | deck.md |
| 融资 BP / VC pitch | [references/bp-deck.md](references/bp-deck.md) | deck.md |
| 自媒体 | [references/social.md](references/social.md) | — |

叠加与加载顺序见 SKILL.md 的路由表；各细则开头也写明了自己继承谁。

当前没有经过用户确认的亲笔文风样本。[已确认偏好与校准方法](references/voice-calibration.md)把王小波式独立思考、故事与幽默，以及半佛仙人、葬AI带来的“活人感”放在中心。其他科技作者的[可迁移技法](references/creator-techniques.md)按选题调用。用户对具体成稿的反馈优先于这份初版画像。

## 安装

my-voice 收录在 [agent-tool-center](https://github.com/roy-tong/agent-tool-center)（第一方 skill 仓库）的 `skills/my-voice/`。克隆一份稳定位置的仓库，再把 skill 软链到用户级目录：

```bash
git clone --depth 1 https://github.com/roy-tong/agent-tool-center.git ~/tools/agent-tool-center
ln -s ~/tools/agent-tool-center/skills/my-voice ~/.agents/skills/my-voice
```

链接到 `~/.agents/skills/` 为用户级（所有项目生效）；只想在单个项目用，链接到该项目的 `.agents/skills/` 或 `.zcode/skills/`。

## 文件结构

```
my-voice/
├── SKILL.md              # 通用底线 + 模式路由 + 输出合同（正本）
└── references/
    ├── report.md         # 报告模式细则
    ├── deck.md           # deck 细则（含图表选型、管理层与经营汇报）
    ├── bp-business.md    # 业务型 BP：证据链、事实标签、页型、生产流程与交付门禁
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
