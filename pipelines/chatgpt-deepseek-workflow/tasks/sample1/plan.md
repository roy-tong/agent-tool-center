# Python 文件扩展名统计 CLI 工具实现方案

## 1. 需求理解（一句话）

实现一个基于 Python 的命令行工具，统计指定目录（递归包含全部子目录）中各文件扩展名对应的文件数量和总大小（字节），将无扩展名文件归类为 `(none)`，默认按文件数量降序输出，并支持通过 `--top N` 限制输出前 N 项。

## 2. 技术选型与理由

- **Python 版本：Python 3.10+**
  - 标准库即可完成全部需求，无需引入第三方依赖。
  - 类型注解、`pathlib`、`dataclasses` 等能力成熟，便于维护和测试。

- **命令行参数：`argparse`**
  - Python 标准库原生支持。
  - 足以处理目录参数、`--top N`、帮助信息及参数校验。
  - 避免为简单 CLI 引入 Click/Typer 等额外依赖。

- **文件遍历：`pathlib.Path.rglob("*")`**
  - 默认满足递归遍历子目录的要求。
  - 相比字符串形式的 `os.path` API，可读性和跨平台性更好。

- **扩展名解析：`Path.suffix`**
  - 统一处理文件扩展名。
  - `foo.txt` → `.txt`
  - `archive.tar.gz` → `.gz`
  - `README` → `(none)`
  - `.gitignore` 按 `pathlib` 语义属于无扩展名文件，因此归入 `(none)`。

- **统计结构：`dict[str, ExtensionStat]`**
  - Key：扩展名，例如 `.py`、`.txt`、`(none)`。
  - Value：该扩展名的文件数量与累计字节数。
  - 单次遍历即可完成统计，时间复杂度约为 `O(F)`，其中 `F` 为文件数量。

- **测试框架：`unittest`**
  - 使用 Python 标准库，不增加项目依赖。
  - 配合 `tempfile.TemporaryDirectory` 构造临时目录及测试文件。

## 3. 实现步骤

1. **创建项目目录结构**

   建议结构：

       file-ext-stats/
       ├── extstats/
       │   ├── __init__.py
       │   ├── scanner.py
       │   └── cli.py
       ├── tests/
       │   ├── __init__.py
       │   ├── test_scanner.py
       │   └── test_cli.py
       ├── pyproject.toml
       └── README.md

   各文件职责：
   - `extstats/scanner.py`：目录扫描、扩展名归类、统计和排序等核心业务逻辑。
   - `extstats/cli.py`：命令行参数解析、参数校验、结果输出。
   - `extstats/__init__.py`：包初始化。
   - `tests/test_scanner.py`：核心统计逻辑测试。
   - `tests/test_cli.py`：CLI 参数和输出行为测试。
   - `pyproject.toml`：项目元信息及 CLI 命令入口。
   - `README.md`：安装及使用说明。

2. **在 `extstats/scanner.py` 中定义统计数据结构**

   定义：

       @dataclass
       class ExtensionStat:
           count: int = 0
           size: int = 0

   字段含义：
   - `count`：该扩展名的文件数量。
   - `size`：该扩展名所有文件的累计大小，单位固定为字节。

   推荐对外统计结果类型：

       dict[str, ExtensionStat]

   示例：

       {
           ".py": ExtensionStat(count=12, size=35840),
           ".txt": ExtensionStat(count=5, size=10240),
           "(none)": ExtensionStat(count=2, size=1536),
       }

3. **实现扩展名归类函数**

   在 `scanner.py` 中创建：

       def get_extension(path: Path) -> str

   处理规则：
   - `test.py` → `.py`
   - `PHOTO.JPG` → `.jpg`
   - `archive.tar.gz` → `.gz`
   - `README` → `(none)`
   - `.gitignore` → `(none)`

   建议统一执行：

       suffix.lower()

   原因是 `.JPG` 和 `.jpg` 通常应统计为同一类型，避免因为大小写产生重复分类。

   如果产品要求严格区分大小写，可去掉 `.lower()`；README 中应明确当前口径。

4. **实现目录扫描与统计函数**

   在 `scanner.py` 中创建：

       def scan_directory(directory: Path) -> dict[str, ExtensionStat]

   执行流程：
   1. 使用 `directory.rglob("*")` 遍历目录及全部子目录。
   2. 使用 `path.is_file()` 排除目录。
   3. 调用 `get_extension(path)` 获取扩展名。
   4. 调用 `path.stat().st_size` 获取文件大小。
   5. 更新对应 `ExtensionStat`：
      - `count += 1`
      - `size += st_size`
   6. 返回完整统计结果。

   注意：
   - 不需要把所有文件路径先加载到列表中，应边遍历边统计，避免大目录产生不必要的内存占用。
   - 文件大小必须使用实际文件的 `st_size`，单位保持为 byte，不自动转换 KB/MB。

5. **处理扫描期间的文件系统异常**

   文件扫描过程中可能出现：
   - 文件被删除。
   - 文件权限不足。
   - 符号链接失效。
   - 文件状态发生变化。

   对单个文件执行 `is_file()` 或 `stat()` 时，应捕获：

       OSError

   推荐策略：
   - 单个文件读取失败时跳过该文件。
   - 向 `stderr` 输出 warning。
   - 不应因为一个不可访问文件导致整个目录统计失败。

   例如逻辑上采用：

       try:
           size = path.stat().st_size
       except OSError as exc:
           warning(...)
           continue

6. **实现排序与 Top N**

   在 `scanner.py` 中增加：

       def sort_stats(
           stats: dict[str, ExtensionStat],
           top: int | None = None,
       ) -> list[tuple[str, ExtensionStat]]

   排序规则建议明确为：
   1. 文件数量 `count` 降序。
   2. 数量相同时按总大小 `size` 降序。
   3. 前两项仍相同时按扩展名字典序升序。

   即排序 Key 等价于：

       (-stat.count, -stat.size, extension)

   这样能够保证结果稳定、可预测，避免同数量情况下由于字典插入顺序造成输出变化。

   当指定 `--top N` 时：
   - 排序完成后返回前 `N` 项。
   - `N` 必须大于 0。
   - `N` 大于扩展名实际数量时，直接返回全部结果。

7. **实现 CLI 参数解析**

   在 `extstats/cli.py` 中创建：

       def build_parser() -> argparse.ArgumentParser

   CLI 定义：

       extstats DIRECTORY [--top N]

   参数：
   - `DIRECTORY`
     - 必填位置参数。
     - 需要统计的目录。
   - `--top N`
     - 可选参数。
     - 仅输出文件数量排名前 N 的扩展名。

   示例：

       extstats .
       extstats /Users/roy/project
       extstats /Users/roy/project --top 10
       extstats . --top 5

   参数校验：
   - DIRECTORY 不存在 → 输出错误并返回非 0 状态码。
   - DIRECTORY 不是目录 → 输出错误并返回非 0 状态码。
   - `--top <= 0` → argparse 参数错误并返回非 0 状态码。

8. **实现程序主入口**

   在 `extstats/cli.py` 中创建：

       def main(argv: list[str] | None = None) -> int

   执行顺序：
   1. 解析参数。
   2. 校验目标目录。
   3. 调用 `scan_directory()`。
   4. 调用 `sort_stats()`。
   5. 格式化输出。
   6. 返回 exit code。

   文件末尾增加：

       if __name__ == "__main__":
           raise SystemExit(main())

9. **定义稳定的输出格式**

   推荐使用纯文本表格，避免第三方依赖。

   输出字段：

       Extension    Files    Bytes
       .py          120      934820
       .json        53       623912
       .md          21       187293
       (none)       8        38723

   要求：
   - `Extension`：扩展名。
   - `Files`：文件数量。
   - `Bytes`：累计文件大小。
   - Bytes 必须输出原始整数，不加入 KB/MB 转换。
   - 不应使用千位分隔符，否则不利于后续 shell 脚本解析。
   - 输出顺序严格遵循排序结果。

   可以创建：

       def print_stats(items: list[tuple[str, ExtensionStat]]) -> None

   将展示逻辑与扫描逻辑分离。

10. **配置可安装的命令行入口**

    创建 `pyproject.toml`，核心配置包括：

        [project]
        name = "file-ext-stats"
        version = "0.1.0"
        requires-python = ">=3.10"

        [project.scripts]
        extstats = "extstats.cli:main"

    安装：

        pip install -e .

    安装完成后即可直接执行：

        extstats /path/to/directory --top 10

    同时应支持：

        python -m extstats.cli /path/to/directory --top 10

11. **编写 `tests/test_scanner.py`**

    使用 `tempfile.TemporaryDirectory` 动态创建测试目录，例如：

        root/
        ├── a.py          # 10 bytes
        ├── b.py          # 20 bytes
        ├── readme        # 5 bytes
        ├── image.JPG     # 30 bytes
        └── sub/
            ├── c.py      # 40 bytes
            └── data.txt  # 50 bytes

    至少覆盖以下测试函数：

       test_get_extension()
       test_scan_directory_recursive()
       test_file_count()
       test_total_size()
       test_no_extension()
       test_case_insensitive_extension()
       test_sort_by_count()
       test_top_n()
       test_top_larger_than_result()

    关键断言：
    - `.py` 文件数量为 3。
    - `.py` 总大小为 70 bytes。
    - `(none)` 数量为 1。
    - `.jpg` 数量为 1。
    - 子目录中的文件确实被统计。

12. **编写 `tests/test_cli.py`**

    测试以下 CLI 场景：
    - 正常目录执行成功。
    - `--top 2` 只输出两条扩展名统计记录。
    - 不存在目录返回错误。
    - 输入普通文件而不是目录返回错误。
    - `--top 0` 返回参数错误。
    - `--top -1` 返回参数错误。

    应尽量直接测试：

        main([...])

    而不是依赖真正启动子进程，使测试更快且更稳定。

13. **创建 `README.md`**

    至少说明：
    - 工具用途。
    - Python 版本要求。
    - 安装方法。
    - 基础调用方法。
    - `--top` 用法。
    - 输出字段含义。
    - 扩展名统计口径。
    - 无扩展名文件归 `(none)`。
    - `.tar.gz` 按 `.gz` 统计。
    - `.gitignore` 等仅有前导点的文件按 `(none)` 统计。
    - 扩展名大小写统一，例如 `.JPG` 与 `.jpg` 合并。
    - 文件读取失败时的处理策略。

14. **执行完整测试与人工验证**

    自动化测试：

        python -m unittest discover -s tests -v

    安装 CLI：

        pip install -e .

    人工测试：

        extstats .
        extstats . --top 5

    最终确认：
    - 递归结果正确。
    - 文件数量正确。
    - 字节数正确。
    - 排序正确。
    - Top N 正确。
    - `(none)` 正确。

## 4. 验收标准

- [ ] 执行 `extstats <directory>` 能成功扫描指定目录。
- [ ] 默认递归统计指定目录下所有层级子目录中的文件。
- [ ] 每种扩展名均输出 `文件数量` 和 `总大小（字节）`。
- [ ] `foo.py` 被正确归类为 `.py`。
- [ ] `foo.txt` 被正确归类为 `.txt`。
- [ ] `archive.tar.gz` 按定义归类为 `.gz`。
- [ ] `README` 被正确归类为 `(none)`。
- [ ] `.gitignore` 被正确归类为 `(none)`。
- [ ] `.JPG` 与 `.jpg` 按设计统一归类为 `.jpg`。
- [ ] 输出默认按照文件数量从高到低排序。
- [ ] 文件数量相同时，排序结果稳定且可重复。
- [ ] 执行 `extstats <directory> --top 5` 最多只输出 5 个扩展名结果。
- [ ] `--top N` 中 N 超过实际扩展名数量时不会报错。
- [ ] `--top 0`、`--top -1` 等非法输入会被拒绝。
- [ ] 指定不存在的目录时返回明确错误信息和非 0 exit code。
- [ ] 指定普通文件而非目录时返回明确错误信息和非 0 exit code。
- [ ] 某个文件由于权限或并发删除无法读取时，不导致整个扫描任务异常退出。
- [ ] `Bytes` 输出的是精确原始字节数，不进行 KB/MB 换算。
- [ ] 对测试目录手工计算的文件数量和总字节数与程序输出完全一致。
- [ ] `python -m unittest discover -s tests -v` 全部测试通过。
- [ ] `pip install -e .` 后可以直接使用 `extstats` 命令。

## 5. 风险与注意事项

- **扩展名定义存在口径问题**
  - 本方案使用 `Path.suffix`，因此 `archive.tar.gz` 统计为 `.gz`，而不是 `.tar.gz`。
  - 这是实现前应固定的产品口径，后续如需识别复合扩展名，应独立增加规则。

- **隐藏文件的扩展名语义**
  - `.gitignore`、`.env` 等只有前导 `.` 的文件，按照 `pathlib` 语义没有 suffix，本方案统一归入 `(none)`。
  - README 中必须明确，避免用户误认为 `.gitignore` 的扩展名是 `.gitignore`。

- **扩展名大小写**
  - Windows/macOS 上用户通常不会认为 `.JPG` 和 `.jpg` 是两种文件类型。
  - 本方案建议通过 `.lower()` 合并统计；如果业务要求严格保留大小写，需要修改 `get_extension()`。

- **符号链接**
  - 需要明确是否统计指向普通文件的符号链接。
  - 建议默认遵循 `pathlib` 当前文件判断行为，但不要递归跟随指向目录的符号链接，避免循环目录导致异常扫描。

- **权限问题**
  - 大型系统目录中可能存在无法访问的文件。
  - 单文件失败应 warning 后跳过，而不是终止整个任务。

- **扫描期间文件变化**
  - 扫描目录过程中，文件可能被新增、删除或修改。
  - 因此结果表示“扫描过程中的近似快照”，不能保证严格的文件系统事务一致性。

- **超大目录性能**
  - 核心扫描复杂度为 `O(F)`，排序复杂度约为 `O(E log E)`，其中 `E` 为不同扩展名数量，通常远小于文件数量。
  - 必须采用流式遍历、即时累加，不要将全部文件路径或文件元数据保存在内存中。

- **文件大小定义**
  - `stat().st_size` 表示文件逻辑大小，不一定等于文件在磁盘上的实际占用空间。
  - 当前需求明确为“总大小（字节）”，因此使用 `st_size` 最合理。

- **Top N 的处理顺序**
  - 必须先完成全量统计和排序，再截取前 N 项。
  - 不能在扫描过程中提前停止，否则无法保证得到真正的 Top N。

- **输出格式的可扩展性**
  - 当前采用人类可读文本表格。
  - 如果未来需要接入 Shell、CI、Agent 或其他程序，建议后续扩展 `--format json` / `--format csv`，但不属于本次 MVP 范围。