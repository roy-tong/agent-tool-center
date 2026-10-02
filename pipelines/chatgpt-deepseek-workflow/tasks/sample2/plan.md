# 开源 Python 库 README.md 模板实现方案

## 1. 需求理解（一句话）

设计一个可直接复制为 `README.md` 使用的通用 Python 开源库 README 模板，覆盖徽章、项目定位、安装、快速开始、API、配置、贡献、许可证等核心内容，并通过内嵌注释明确各部分的撰写原则和替换项。

## 2. 技术选型与理由

- **文件格式：Markdown**
  - GitHub、GitLab、PyPI 等平台原生支持。
  - 无额外构建依赖，复制后即可使用。
  - 支持代码块、表格、链接、图片、徽章等 README 常用元素。

- **模板变量：`{{VARIABLE_NAME}}`**
  - 例如 `{{PROJECT_NAME}}`、`{{PACKAGE_NAME}}`、`{{GITHUB_OWNER}}`。
  - 与普通 Markdown 内容区分明显，便于人工替换或后续通过脚本自动生成。
  - 不绑定 Jinja2 等模板引擎，保持模板本身零依赖。

- **撰写提示：HTML 注释 `<!-- ... -->`**
  - GitHub 渲染时不会展示。
  - README 维护者编辑源文件时可以直接看到说明。
  - 可以在模板保留“如何写这一节”的指导，而不污染最终展示效果。

- **徽章：Shields.io + GitHub Actions + PyPI**
  - 覆盖构建状态、PyPI 版本、Python 版本、许可证等开源 Python 项目最常见信息。
  - 模板只提供通用结构，不强制项目必须启用全部徽章。

- **示例代码：Python fenced code block**
  - 所有示例优先采用“最小可运行示例”，避免 README 演变成完整 API 文档。
  - API 详细文档可进一步链接到 `docs/`、MkDocs 或 Sphinx。

## 3. 实现步骤

1. **创建模板文件 `README.template.md`**

   职责：
   - 作为所有 Python 开源项目 README 的基础模板。
   - 提供标准章节结构。
   - 提供可替换变量。
   - 通过 HTML 注释说明每一部分的撰写方法。

   使用以下完整内容：

~~~~markdown
# {{PROJECT_NAME}}

<!--
撰写要点：
1. 项目名称应与 PyPI/GitHub 中的名称尽量保持一致。
2. 标题下不要立即堆大量文字，先通过徽章和一句话定位让用户快速理解项目。
-->

[![PyPI version](https://img.shields.io/pypi/v/{{PYPI_PACKAGE_NAME}})](https://pypi.org/project/{{PYPI_PACKAGE_NAME}}/)
[![Python versions](https://img.shields.io/pypi/pyversions/{{PYPI_PACKAGE_NAME}})](https://pypi.org/project/{{PYPI_PACKAGE_NAME}}/)
[![CI](https://github.com/{{GITHUB_OWNER}}/{{GITHUB_REPO}}/actions/workflows/ci.yml/badge.svg)](https://github.com/{{GITHUB_OWNER}}/{{GITHUB_REPO}}/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/{{GITHUB_OWNER}}/{{GITHUB_REPO}})](LICENSE)

<!--
徽章区撰写要点：
- 建议保留 3～5 个真正有价值的徽章，不要堆砌。
- 推荐优先级：
  1. PyPI Version
  2. CI/Test Status
  3. Python Version
  4. License
  5. Coverage（如项目实际使用）
- 如果项目未发布 PyPI，删除对应徽章。
- 如果 CI workflow 文件不是 ci.yml，请修改链接。
-->

> {{ONE_LINE_DESCRIPTION}}

<!--
项目一句话描述：
用一句话回答：
“这个项目是什么，它帮助谁解决什么问题？”

推荐格式：
“A Python library for ...”

不要使用：
“A powerful / awesome / next-generation library...”
这类没有提供实际信息的营销表达。
-->

## Overview

{{PROJECT_DESCRIPTION}}

<!--
项目简介撰写要点：

建议回答四个问题：
1. 这个库解决什么问题？
2. 为什么需要它？
3. 它与已有方案相比有什么特点？
4. 谁适合使用它？

建议控制在 2～4 个自然段。

如有明确核心能力，可补充：

Key features:

- Feature A
- Feature B
- Feature C

避免直接在这里写大量技术实现细节。
-->

### Features

- {{FEATURE_1}}
- {{FEATURE_2}}
- {{FEATURE_3}}

<!--
Feature 应描述用户获得的能力，而不仅是内部技术实现。

较好：
- Async HTTP requests with automatic retries

较差：
- Uses asyncio
-->

## Installation

### From PyPI

```bash
pip install {{PYPI_PACKAGE_NAME}}

### With optional dependencies
```
pip install "{{PYPI_PACKAGE_NAME}}[{{EXTRA_NAME}}]"
```


### From source
```
git clone https://github.com/{{GITHUB_OWNER}}/{{GITHUB_REPO}}.git
cd {{GITHUB_REPO}}
pip install -e .
```


### Requirements

- Python >= {{MINIMUM_PYTHON_VERSION}}
  
- {{OPTIONAL_SYSTEM_REQUIREMENT}}
  

## Quick Start
```
from {{PACKAGE_NAME}} import {{PRIMARY_API}}

{{QUICK_START_CODE}}
```

Expected output:
```
{{QUICK_START_OUTPUT}}
```


## API Examples

### {{API_EXAMPLE_1_NAME}}
```
from {{PACKAGE_NAME}} import {{API_OBJECT}}

{{API_EXAMPLE_1_CODE}}
```

{{API_EXAMPLE_1_DESCRIPTION}}

### {{API_EXAMPLE_2_NAME}}
```
{{API_EXAMPLE_2_CODE}}
```

{{API_EXAMPLE_2_DESCRIPTION}}

## Configuration
{{PROJECT_NAME}} can be configured using {{CONFIGURATION_METHOD}}.
Example:
```
{{CONFIG_EXAMPLE}}
```

Or using environment variables:
```
export {{ENV_PREFIX}}_{{CONFIG_KEY}}="{{CONFIG_VALUE}}"
```


### Configuration options
Option	Type	Default	Description
{{OPTION_1}}	{{TYPE_1}}	{{DEFAULT_1}}	{{DESCRIPTION_1}}
{{OPTION_2}}	{{TYPE_2}}	{{DEFAULT_2}}	{{DESCRIPTION_2}}
{{OPTION_3}}	{{TYPE_3}}	{{DEFAULT_3}}	{{DESCRIPTION_3}}


## Documentation
Full documentation is available at:
{{DOCUMENTATION_URL}}

## Development
Clone the repository:
```
git clone https://github.com/{{GITHUB_OWNER}}/{{GITHUB_REPO}}.git
cd {{GITHUB_REPO}}
```

Create a virtual environment:
```
python -m venv .venv
source .venv/bin/activate
```

Install development dependencies:
```
pip install -e ".[dev]"
```

Run tests:
```
pytest
```

Run linting:
```
{{LINT_COMMAND}}
```


## Contributing
Contributions are welcome.
Before submitting a pull request:

1. Fork the repository.
  
2. Create a feature branch:
  ```
git checkout -b feature/your-feature
```

  
3. Add or update tests.
  
4. Ensure all tests pass:
  ```
pytest
```

  
5. Ensure code quality checks pass:
  ```
{{LINT_COMMAND}}
```

  
6. Commit your changes.
  
7. Push your branch and open a pull request.
  
For larger changes, please open an issue first to discuss the proposed design.
See [CONTRIBUTING.md]() for detailed contribution guidelines.

## Project Structure
```
{{GITHUB_REPO}}/
├── src/
│   └── {{PACKAGE_NAME}}/
├── tests/
├── docs/
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```


## Compatibility
Python	Supported
{{PYTHON_VERSION_1}}	✅
{{PYTHON_VERSION_2}}	✅
{{PYTHON_VERSION_3}}	✅


## Roadmap

- {{ROADMAP_ITEM_1}}
  
- {{ROADMAP_ITEM_2}}
  
- {{ROADMAP_ITEM_3}}
  

## FAQ

### {{FAQ_QUESTION_1}}
{{FAQ_ANSWER_1}}

### {{FAQ_QUESTION_2}}
{{FAQ_ANSWER_2}}

## Security
If you discover a security vulnerability, please do **not** open a public issue.
Please follow the instructions in [SECURITY.md]().

## License
This project is licensed under the {{LICENSE_NAME}} License.
See [LICENSE]() for details.

## Acknowledgements

- {{ACKNOWLEDGEMENT_1}}
  
- {{ACKNOWLEDGEMENT_2}}
  

Maintained by [{{MAINTAINER_NAME}}]().
```
2. **定义模板变量替换规则**

   建议至少支持以下变量：

   | 变量 | 含义 | 示例 |
   |---|---|---|
   | `{{PROJECT_NAME}}` | 对外展示项目名 | `FastCache` |
   | `{{PYPI_PACKAGE_NAME}}` | PyPI 包名 | `fastcache` |
   | `{{PACKAGE_NAME}}` | Python import 包名 | `fastcache` |
   | `{{GITHUB_OWNER}}` | GitHub 用户或组织 | `example-org` |
   | `{{GITHUB_REPO}}` | GitHub 仓库名 | `fastcache` |
   | `{{ONE_LINE_DESCRIPTION}}` | 一句话项目定位 | `A lightweight cache library for Python.` |
   | `{{MINIMUM_PYTHON_VERSION}}` | 最低 Python 版本 | `3.10` |
   | `{{LICENSE_NAME}}` | 开源许可证 | `MIT` |
   | `{{DOCUMENTATION_URL}}` | 文档地址 | `https://example.org/docs` |

   变量设计原则：
   - 全部采用大写 snake case。
   - 同一含义只定义一个变量。
   - 不把大段 Markdown 内容抽象成变量。
   - 发布前必须确保不存在未替换变量。

3. **按“必要章节”和“可选章节”管理模板**

   必须保留：

   ```text
   Project Name
   Badges
   One-line Description
   Overview
   Installation
   Quick Start
   API Examples
   Configuration
   Contributing
   License
   ```

   根据项目情况保留：

   ```text
   Documentation
   Development
   Project Structure
   Compatibility
   Roadmap
   FAQ
   Security
   Acknowledgements
   ```

   原则是 README 服务于“第一次接触项目的用户”，而不是承担项目所有文档职责。

4. **创建 `CONTRIBUTING.md`（推荐）**

   职责：
   - 承载 README 中不宜展开的完整贡献规则。
   - 定义开发环境、测试、代码规范、Issue 和 PR 流程。

   README 只保留贡献入口及最小流程，避免主文档过长。

5. **创建 `LICENSE`**

   职责：
   - 存放项目实际采用的标准许可证全文。
   - README 中的 `{{LICENSE_NAME}}` 必须与其一致。

   不应只在 README 中声明 License 而遗漏仓库根目录的许可证文件。

6. **实际使用模板时执行一次初始化替换**

   ```bash
   cp README.template.md README.md
   ```

   然后全局查找：

   ```text
   {{
   ```

   依次替换所有变量，并删除不适用于当前项目的可选章节和 HTML 编写提示。

7. **最终检查 README 信息架构**

   推荐最终阅读路径应当形成：

   ```text
   这是什么？
       ↓
   为什么值得使用？
       ↓
   怎么安装？
       ↓
   怎么在几分钟内跑起来？
       ↓
   常见任务怎么实现？
       ↓
   怎么配置？
       ↓
   去哪里找完整文档？
       ↓
   怎么参与开发？
       ↓
   使用什么许可证？
   ```

   如果一个新用户无法沿该路径快速理解项目，则应继续简化 README，而不是继续增加章节。

## 4. 验收标准

- [ ] 仓库中存在可直接复制使用的 `README.template.md`。
- [ ] README 包含项目名称及一句话项目定位。
- [ ] README 包含徽章区域。
- [ ] 至少包含 PyPI Version、CI、Python Version、License 四类常用徽章模板。
- [ ] README 包含项目简介 `Overview`。
- [ ] README 包含 `Installation`。
- [ ] 安装章节至少提供标准 `pip install` 示例。
- [ ] README 包含 `Quick Start`。
- [ ] Quick Start 提供完整 Python 示例，而非伪代码说明。
- [ ] README 包含 `API Examples`。
- [ ] API 示例按照用户任务/使用场景组织，而非简单罗列类名和函数名。
- [ ] README 包含 `Configuration`。
- [ ] 配置部分说明配置方式、配置项、类型、默认值和含义。
- [ ] README 包含 `Contributing`。
- [ ] README 包含 `License`，并链接根目录 `LICENSE` 文件。
- [ ] 每个核心章节均通过 HTML 注释写明该部分的撰写要点。
- [ ] HTML 注释不会出现在 GitHub 最终渲染结果中。
- [ ] 模板变量统一采用 `{{UPPER_SNAKE_CASE}}`。
- [ ] README 发布前搜索 `{{` 的结果为 0，确保不存在未替换变量。
- [ ] 所有 README 内部链接均有效。
- [ ] 所有徽章 URL 均可访问。
- [ ] `pip install` 安装命令已实际验证。
- [ ] Quick Start 已在全新 Python 环境中实际运行成功。
- [ ] README 示例与当前公开 API 一致。
- [ ] README 中声明的最低 Python 版本与 `pyproject.toml` 一致。
- [ ] README 中声明的 License 与实际 `LICENSE` 文件一致。
- [ ] 删除了所有与当前项目无关的可选章节，不保留空章节。
- [ ] 用户无需阅读源码即可在 3～5 分钟内完成“理解项目 → 安装 → 第一次成功调用”。

## 5. 风险与注意事项

1. **避免 README 过度模板化**
   - 模板提供的是信息架构，而不是要求所有项目保留所有章节。
   - 小型库应主动删除 Roadmap、FAQ、Project Structure 等无实际信息的章节。

2. **Quick Start 是最高优先级内容**
   - 最常见的问题不是 README 缺少章节，而是示例无法运行。
   - 每次 API Breaking Change 后都应将 README 示例纳入回归检查。

3. **不要让 README 替代正式文档**
   - README 负责降低第一次使用门槛。
   - 大型 API Reference、Architecture、Tutorial 应迁移至 `docs/`。

4. **模板变量存在遗漏风险**
   - 发布前必须全局搜索 `{{`。
   - 可进一步在 CI 中增加检查，发现模板占位符后阻止发布。

5. **徽章必须反映真实状态**
   - 不存在 PyPI 包时不要展示 PyPI 徽章。
   - 未启用 Coverage 时不要添加 Coverage Badge。
   - CI workflow 路径必须与 `.github/workflows/` 中实际文件一致。

6. **README 与代码可能发生版本漂移**
   - 安装命令和 Quick Start 建议加入 CI smoke test。
   - README 中涉及公开 API 的示例应作为可执行代码维护，而不是长期无人验证的文档片段。

7. **安全信息不要写入示例**
   - API Key、Token、Password 等统一使用占位值或环境变量。
   - 不得提交任何真实凭证。

8. **许可证必须明确**
   - GitHub 仓库公开不等于自动获得开源许可证。
   - 若项目计划真正开源，应明确选择 License，并在仓库根目录提供标准 `LICENSE` 文件。
```
```