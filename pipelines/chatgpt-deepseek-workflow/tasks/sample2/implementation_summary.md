# 实现产物清单

````text
README.template.md
````

## 文件: README.template.md
````
<!--
============================================================
 开源 Python 库 README 模板
 使用方法：
   1. 全文搜索并替换 {{VARIABLE_NAME}} 占位符（见下方清单）。
   2. 删除不适用的小节与 HTML 注释。
   3. 将本文件内容粘贴为项目根目录的 README.md。
 占位符清单：
   {{PROJECT_NAME}}        项目显示名（与 PyPI/GitHub 名称保持一致）
   {{PYPI_PACKAGE_NAME}}   PyPI 上的包名（pip install 用，可能含连字符）
   {{IMPORT_NAME}}         Python import 模块名（下划线命名，如 my_awesome_lib）
   {{GITHUB_OWNER}}        GitHub 用户名/组织
   {{GITHUB_REPO}}         GitHub 仓库名
   {{TAGLINE}}             一句话项目定位
   {{MIN_PYTHON}}          最低 Python 版本，如 3.9
   {{LICENSE_NAME}}        许可证名称，如 MIT
   {{ENV_VAR}}             配置项环境变量名（配置说明小节，可选）
   {{DEFAULT}}             配置项默认值（配置说明小节，可选）
   {{YEAR}}                当前年份（许可证小节）
   {{AUTHOR_NAME}}         作者/版权持有者名称（许可证小节）
   {{DEV_INSTALL_COMMAND}}  开发依赖安装命令（贡献指南，如 pip install -e ".[dev]"）
   {{TEST_COMMAND}}         测试命令（贡献指南，如 pytest）
   {{LINT_COMMAND}}         代码检查命令（贡献指南，如 pre-commit run --all-files）

 使用前检查清单：
   [ ] 所有 {{...}} 占位符已替换（可在编辑器里搜索 "{{" 确认无遗漏）
   [ ] 徽章链接中的仓库名/包名与真实地址一致
   [ ] 快速开始示例在本机实际运行过
   [ ] 删除了不适用的小节与全部 HTML 注释
   [ ] 用 Markdown 预览（GitHub/本地）检查渲染无异常
============================================================
-->

# {{PROJECT_NAME}}

<!-- 撰写要点：
1. 标题下方不要堆大段文字，先给徽章 + 一句话定位，让读者 3 秒内判断项目是否相关。
2. 徽章只保留真正有意义的 3~5 个（构建状态 / 版本 / 覆盖率 / 许可证），不要堆砌。
-->

[![PyPI version](https://img.shields.io/pypi/v/{{PYPI_PACKAGE_NAME}})](https://pypi.org/project/{{PYPI_PACKAGE_NAME}}/)
[![Python versions](https://img.shields.io/pypi/pyversions/{{PYPI_PACKAGE_NAME}})](https://pypi.org/project/{{PYPI_PACKAGE_NAME}}/)
[![CI](https://github.com/{{GITHUB_OWNER}}/{{GITHUB_REPO}}/actions/workflows/ci.yml/badge.svg)](https://github.com/{{GITHUB_OWNER}}/{{GITHUB_REPO}}/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/{{GITHUB_OWNER}}/{{GITHUB_REPO}})](LICENSE)

<!-- 项目简介：用 1~2 句话说明"这是什么、解决什么问题、为什么比替代方案好"。 -->
**{{TAGLINE}}**

{{PROJECT_NAME}} 是一个……（解决的问题）。它……（核心特性，3 条以内，用列表）：

- ✨ 特性一：……
- ⚡ 特性二：……
- 🛠 特性三：……

## 安装

<!-- 撰写要点：给出最常用的安装命令；如有额外依赖（如 pipx / uv），单独说明。 -->

```bash
pip install {{PYPI_PACKAGE_NAME}}
```

要求 Python {{MIN_PYTHON}}+。

## 快速开始

<!-- 撰写要点：
1. 给一个"最小可运行示例"：复制粘贴即可跑通——输入、API、预期输出都要具体。
2. 不要在这里展开完整 API 文档，详细内容放"API 示例"小节或链接到 docs/。
-->

```python
import {{IMPORT_NAME}}

# 最小示例：替换为项目真实的最短调用链
result = {{IMPORT_NAME}}.do_something("具体输入值", limit=10)
print(result)  # 预期输出示例：['结果1', '结果2', ...]
```

## API 示例

<!-- 撰写要点：按使用频率排列常用 API，每个给出签名、参数说明与输出示例。
表格适合参数较多的场景；代码块适合展示典型调用链。 -->

### `do_something(arg1, arg2=None)`

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `arg1` | `str` | 必填，…… |
| `arg2` | `Optional[int]` | 可选，默认 `None`，…… |

```python
{{IMPORT_NAME}}.do_something("示例", arg2=42)
# => 输出示例
```

## 配置说明

<!-- 撰写要点：列出环境变量、配置文件或参数选项，说明默认值与作用。
没有配置项的库可以删除本节。 -->

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `{{ENV_VAR}}` | `{{DEFAULT}}` | …… |

## 贡献指南

<!-- 撰写要点：
1. 说明开发环境搭建（克隆、安装 dev 依赖、跑测试）。
2. 代码风格与提交规范用 {{...}} 占位符配置化，按项目实际技术栈替换。
3. 说明 PR 流程（分支、测试、文档要求）。
-->

欢迎贡献！请遵循以下流程：

1. Fork 本仓库并创建特性分支。
2. 安装开发依赖：`{{DEV_INSTALL_COMMAND}}`（如 `pip install -e ".[dev]"`）。
3. 运行测试：`{{TEST_COMMAND}}`（如 `pytest`）。
4. 提交前运行代码检查：`{{LINT_COMMAND}}`（如 `pre-commit run --all-files`，如已配置）。
5. 提交 PR 时说明改动动机与验证方式。

## 许可证

<!-- 撰写要点：
1. 明确许可证名称并链接 LICENSE 文件。
2. 如需概述授权范围，必须与许可证原文一致；LICENSE 文件始终是最终法律依据。
-->

本项目基于 [{{LICENSE_NAME}}](LICENSE) 发布，具体使用、修改和分发条件请参阅 LICENSE 文件。

© {{YEAR}} {{AUTHOR_NAME}}

<!-- 以下为可选小节（按需保留或删除）：

## 文档

完整文档见 [docs](https://{{GITHUB_OWNER}}.github.io/{{GITHUB_REPO}}/) / Read the Docs。

## 常见问题

### 问题 1？
回答……

## 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)。

## 致谢

感谢…… 
-->
````
