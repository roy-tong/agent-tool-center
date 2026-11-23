# my-voice

个人默认表达优化 skill，用于 Claude Code / ZCode 等 agent（兼容 [Agent Skills](https://code.claude.com/docs/en/skills) 规范：目录 + SKILL.md + 按需加载的 references）。

管官网与 GTM 营销材料（含 GitHub Profile、仓库 README、发布页）、报告、普通 deck（含管理层汇报）、业务 BP、融资 BP 和公开写作的从零创作与常规改写。通用底线、场景路由和输出合同以 [SKILL.md](SKILL.md) 为唯一正本，本 README 只做安装与结构导航。

## 当前版本

当前发行版本：[`my-voice-v2.1.0`](https://github.com/roy-tong/agent-tool-center/releases/tag/my-voice-v2.1.0)（2026-11-23）。

| 材料 | 文件 | 状态 |
| --- | --- | --- |
| 通用底线、场景路由与交付合同 | [SKILL.md](SKILL.md) | 现行 |
| 页级内容合同、图表与生产核验 | [references/deck.md](references/deck.md) | 现行 |
| Slidev/Presenton 生成、导出与双重审计 | [references/deck-production.md](references/deck-production.md) | 现行，工具能力核对日期 2026-11-22 |
| 中英文业务语言与双语示例 | [references/business-language.md](references/business-language.md) | 现行 |
| 官网、GitHub Profile、仓库 README 与 GTM 叙事 | [references/gtm.md](references/gtm.md) | 现行 |
| 广告与 VC 传播研究、slogan 与信息屋 | [references/persuasion-research.md](references/persuasion-research.md) | 现行，研究核对日期 2026-11-23 |
| 融资叙事、投资论点与异议驱动页序 | [references/bp-deck.md](references/bp-deck.md) | 现行 |
| VC 官方建议与公开 BP 案例研究 | [references/bp-investor-research.md](references/bp-investor-research.md) | 现行，研究核对日期 2026-11-22 |
| 业务型 BP 证据链与多版式 | [references/bp-business.md](references/bp-business.md) | 现行 |
| 历史版本与旧 release notes | `90-历史版本/` | 留档，不作为当前规则 |

## 场景与细则

| 场景 | 主细则 | 继承 |
| --- | --- | --- |
| 官网、GitHub 首页、仓库 README 与 GTM | [references/gtm.md](references/gtm.md) | persuasion-research.md + business-language.md |
| 报告 | [references/report.md](references/report.md) | — |
| 中英文商业表达 / 去机翻 | [references/business-language.md](references/business-language.md) | SKILL.md |
| deck（普通 + 管理层 / 经营汇报） | [references/deck.md](references/deck.md) | business-language.md |
| 实际 PPTX/PDF、Slidev/Presenton 生产 | [references/deck-production.md](references/deck-production.md) | deck.md + deck-design |
| 业务型 BP / 多产品族方案 | [references/bp-business.md](references/bp-business.md) | deck.md + business-language.md |
| 融资 BP / VC pitch | [references/bp-deck.md](references/bp-deck.md) | deck.md + business-language.md |
| VC 方法与公开 BP 案例 | [references/bp-investor-research.md](references/bp-investor-research.md) | 融资任务按需加载 |
| 自媒体 | [references/social.md](references/social.md) | — |

叠加与加载顺序见 SKILL.md 的路由表；各细则开头也写明了自己继承谁。

实际 PPTX 或版式重排必须同时使用 `deck-design`，生成与导出按 [Deck 生产架构](references/deck-production.md)：新代码型 Deck 默认 Slidev，GUI/可编辑交付优先 Presenton，Marp 为轻量备选，python-pptx 留给存量与高度定制原生图表。`deck-scaffold` 只维护存量，不用于新项目。完整顺序是：事实账本 → 主线 → 页级内容合同 → 图表与语言 → 内容/视觉锁 → Slidev/Presenton → 实际 PPTX 几何审计 → 成品 PNG 复核。`deck-humanizer` 只负责专项文案去味，不替代叙事、证据或设计。

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
    ├── business-language.md # 中英文业务语言、伪 VC 腔清理与双语示例
    ├── deck.md           # 页级内容合同、信息密度、图表与生产核验
    ├── deck-production.md # Slidev/Presenton 路由、内容/视觉锁、导出与审计
    ├── bp-business.md    # 业务型 BP：证据链、事实标签、页型、生产流程与交付门禁
    ├── bp-deck.md        # 融资 BP：投资论点、异议、页序、市场、团队与口径
    ├── bp-investor-research.md # VC 一手建议与公开 BP 案例的可迁移方法
    ├── gtm.md            # 官网/README/GTM：愿景、目标价值、采用理由与披露分工
    ├── persuasion-research.md # 4A 广告方法与 VC 叙事、信息屋与 slogan 候选
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
