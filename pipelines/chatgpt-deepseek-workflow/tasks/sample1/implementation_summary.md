# 实现产物清单

```text
extstats/__init__.py
extstats/cli.py
extstats/scanner.py
pyproject.toml
README.md
tests/__init__.py
tests/test_cli.py
tests/test_scanner.py
```

## 文件: extstats/__init__.py
```
"""file-ext-stats 包初始化。"""
from .scanner import ExtensionStat, get_extension, scan_directory, sort_stats

__all__ = ["ExtensionStat", "get_extension", "scan_directory", "sort_stats"]
__version__ = "0.1.0"
```

## 文件: extstats/cli.py
```
"""文件扩展名统计工具 CLI 入口：参数解析、校验、调用核心逻辑、格式化输出。"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .scanner import ExtensionStat, scan_directory, sort_stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="extstats",
        description="统计目录下各文件扩展名的文件数量与总大小（字节），默认递归子目录。",
    )
    parser.add_argument("directory", type=Path, help="需要统计的目标目录")
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="仅输出文件数量排名前 N 的扩展名（必须大于 0）",
    )
    return parser


def print_stats(items: list[tuple[str, ExtensionStat]]) -> None:
    """输出纯文本表格：Extension / Files / Bytes（原始字节数，无千位分隔符）。"""
    header = ("Extension", "Files", "Bytes")
    rows = [(ext, str(st.count), str(st.size)) for ext, st in items]
    widths = [
        max(len(row[i]) for row in rows + [header])
        for i in range(3)
    ]
    line = "  ".join(f"{cell:<{widths[i]}}" for i, cell in enumerate(header))
    print(line)
    print("-" * len(line))
    for row in rows:
        print("  ".join(f"{cell:<{widths[i]}}" for i, cell in enumerate(row)))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    directory: Path = args.directory
    if not directory.exists():
        parser.error(f"directory does not exist: {directory}")
    if not directory.is_dir():
        parser.error(f"path is not a directory: {directory}")
    if args.top is not None and args.top <= 0:
        parser.error("--top must be greater than 0")

    stats = scan_directory(directory)
    results = sort_stats(stats, top=args.top)
    print_stats(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## 文件: extstats/scanner.py
```
"""文件扩展名统计工具（file-ext-stats）核心扫描逻辑。

职责：目录扫描、扩展名归类、统计、排序 —— 不处理命令行参数、不负责展示。
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class ExtensionStat:
    """一种扩展名的统计结果。"""

    count: int = 0
    size: int = 0


def get_extension(path: Path) -> str:
    """返回统一小写的扩展名；无扩展名的文件归为 '(none)'。

    口径（与方案一致）：
    - foo.py            -> '.py'
    - PHOTO.JPG         -> '.jpg'（统一小写）
    - archive.tar.gz    -> '.gz'（取最后一个扩展名）
    - README            -> '(none)'
    - .gitignore        -> '(none)'（pathlib 语义下无 suffix）
    """
    suffix = path.suffix.lower()
    return suffix if suffix else "(none)"


def _onerror(exc: OSError) -> None:
    """目录遍历阶段出错（权限/并发删除等）→ 告警并继续，不让单个目录拖垮整体扫描。"""
    print(f"warning: 无法遍历目录（{exc}），已跳过", file=sys.stderr)


def iter_files(root: Path) -> Iterator[Path]:
    """递归遍历目录下所有文件（默认递归）。

    用 os.walk + onerror 明确处理目录遍历错误；文件读取错误由调用方按文件捕获。
    """
    for dirpath, _dirnames, filenames in os.walk(root, onerror=_onerror):
        base = Path(dirpath)
        for name in filenames:
            path = base / name
            try:
                if path.is_file():
                    yield path
            except OSError:
                # 单文件不可访问（权限/失效符号链接/并发删除）→ 跳过并告警
                print(f"warning: 无法访问 {path}，已跳过", file=sys.stderr)


def scan_directory(directory: Path) -> dict[str, ExtensionStat]:
    """扫描目录并统计各扩展名的文件数量与总字节数（流式，不缓存全部路径）。"""
    stats: dict[str, ExtensionStat] = defaultdict(ExtensionStat)
    for path in iter_files(directory):
        extension = get_extension(path)
        try:
            size = path.stat().st_size
        except OSError as exc:
            print(f"warning: 无法读取 {path} 的大小（{exc}），已跳过", file=sys.stderr)
            continue
        stats[extension].count += 1
        stats[extension].size += size
    return dict(stats)


def sort_stats(
    stats: dict[str, ExtensionStat],
    top: int | None = None,
) -> list[tuple[str, ExtensionStat]]:
    """排序：文件数量降序 → 总大小降序 → 扩展名字典序升序；再按 top 截取。"""
    if top is not None and top <= 0:
        raise ValueError("top must be greater than 0")
    results = sorted(
        stats.items(),
        key=lambda item: (-item[1].count, -item[1].size, item[0]),
    )
    if top is not None:
        results = results[:top]
    return results
```

## 文件: pyproject.toml
```
[project]
name = "file-ext-stats"
version = "0.1.0"
description = "统计目录下各文件扩展名的文件数量与总大小（字节）的 CLI 工具"
requires-python = ">=3.10"

[project.scripts]
extstats = "extstats.cli:main"

[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["extstats*"]
```

## 文件: README.md
```
# file-ext-stats

统计目录下各文件扩展名的**文件数量**与**总大小（字节）**的命令行工具，默认递归扫描子目录。

## 环境要求

- Python 3.10+

## 安装

```bash
pip install -e .
```

## 使用

```bash
# 统计当前目录
extstats .

# 统计指定目录
extstats /path/to/project

# 只看文件数量前 5 名的扩展名
extstats . --top 5

# 查看帮助
extstats --help
```

也可以不安装直接运行：

```bash
python -m extstats.cli . --top 5
```

## 输出说明

```
Extension    Files    Bytes
-----------------------------
.py          120      934820
.json        53       623912
.md          21       187293
(none)       8        38723
```

- `Extension`：扩展名（统一小写）
- `Files`：文件数量
- `Bytes`：累计文件大小（原始字节数，不做 KB/MB 换算，无千位分隔符）
- 排序规则：文件数量降序 → 总大小降序 → 扩展名字典序升序

## 统计口径

| 文件 | 归类 | 说明 |
| --- | --- | --- |
| `foo.py` | `.py` | 常规扩展名 |
| `archive.tar.gz` | `.gz` | 取最后一个扩展名 |
| `README` / `Makefile` | `(none)` | 无扩展名 |
| `.gitignore` / `.env` | `(none)` | 仅有前导点的文件按 `pathlib` 语义无扩展名 |
| `PHOTO.JPG` | `.jpg` | 扩展名统一小写，与 `photo.jpg` 合并统计 |

## 异常处理

- 目录遍历阶段出错（子目录无权限、被并发删除等）时输出 warning 到 stderr 并跳过该目录，不影响整体统计。
- 单个文件因权限、并发删除等原因无法读取时，输出 warning 到 stderr 并跳过，不影响整体统计。
- 目录不存在 / 不是目录 / `--top <= 0` 时返回明确错误和非 0 退出码。
- 空目录只输出表头，不输出数据行。
- 符号链接：文件符号链接按其目标文件统计；目录符号链接不递归跟随（`os.walk` 默认行为），避免循环。

## 测试

```bash
python -m unittest discover -s tests -v
```
```

## 文件: tests/__init__.py
```
```

## 文件: tests/test_cli.py
```
"""CLI 参数与输出行为测试。"""
import tempfile
import unittest
from pathlib import Path

from extstats.cli import main


class TestCli(unittest.TestCase):
    def _run(self, *argv):
        """直接调用 main([...])，不启动子进程。"""
        import contextlib
        import io

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main(list(argv))
        return code, out.getvalue()

    def _make_tree(self, root: Path) -> None:
        (root / "a.py").write_bytes(b"12345")
        (root / "b.py").write_bytes(b"12345")
        (root / "c.txt").write_bytes(b"x" * 15)
        (root / "README").write_bytes(b"12345")

    def test_normal_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_tree(Path(tmp))
            code, out = self._run(tmp)
            self.assertEqual(code, 0)
            self.assertIn(".py", out)
            self.assertIn("(none)", out)

    def test_top_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_tree(Path(tmp))
            code, out = self._run(tmp, "--top", "2")
            self.assertEqual(code, 0)
            rows = [l for l in out.splitlines() if l.strip() and not l.startswith("-")]
            self.assertEqual(len(rows), 3)  # header + 2 rows

    def test_cli_output_sorted_by_count_desc(self):
        """端到端：输出行的扩展名顺序必须与排序规则一致（.py×2 > .txt×1 == (none)×1）。"""
        with tempfile.TemporaryDirectory() as tmp:
            self._make_tree(Path(tmp))
            code, out = self._run(tmp)
            self.assertEqual(code, 0)
            data_rows = [l for l in out.splitlines() if l.strip() and not l.startswith("-")][1:]
            extensions = [row.split()[0] for row in data_rows]
            self.assertEqual(extensions[0], ".py")  # 数量最多排第一
            # .txt 与 (none) 数量相同 → 按总大小降序（.txt 15B > (none) 5B）
            self.assertEqual(extensions[1:], [".txt", "(none)"])

    def test_cli_output_size_correct(self):
        """端到端：Bytes 数值必须等于实际累计字节（a.py 5B + b.py 5B = 10B）。"""
        with tempfile.TemporaryDirectory() as tmp:
            self._make_tree(Path(tmp))
            code, out = self._run(tmp)
            self.assertEqual(code, 0)
            data_rows = [l for l in out.splitlines() if l.strip() and not l.startswith("-")][1:]
            py_row = next(r for r in data_rows if r.split()[0] == ".py")
            self.assertEqual(py_row.split()[1:], ["2", "10"])

    def test_top_2_keeps_top_extensions(self):
        """端到端：--top 2 保留的必须是排序后的前 2 名扩展名。"""
        with tempfile.TemporaryDirectory() as tmp:
            self._make_tree(Path(tmp))
            code, out = self._run(tmp, "--top", "2")
            self.assertEqual(code, 0)
            data_rows = [l for l in out.splitlines() if l.strip() and not l.startswith("-")][1:]
            extensions = [row.split()[0] for row in data_rows]
            self.assertEqual(extensions, [".py", ".txt"])

    def test_empty_directory(self):
        """端到端：空目录正常退出，只输出表头。"""
        with tempfile.TemporaryDirectory() as tmp:
            code, out = self._run(tmp)
            self.assertEqual(code, 0)
            lines = [l for l in out.splitlines() if l.strip()]
            self.assertEqual(len(lines), 2)  # 表头 + 分隔线，无数据行

    def test_nonexistent_directory(self):
        with self.assertRaises(SystemExit) as cm:
            main(["/no/such/dir/xyz"])
        self.assertNotEqual(cm.exception.code, 0)

    def test_file_not_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "a.py"
            f.write_text("x")
            with self.assertRaises(SystemExit) as cm:
                main([str(f)])
            self.assertNotEqual(cm.exception.code, 0)

    def test_top_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_tree(Path(tmp))
            with self.assertRaises(SystemExit) as cm:
                main([tmp, "--top", "0"])
            self.assertNotEqual(cm.exception.code, 0)

    def test_top_negative(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_tree(Path(tmp))
            with self.assertRaises(SystemExit) as cm:
                main([tmp, "--top", "-1"])
            self.assertNotEqual(cm.exception.code, 0)

    def test_bytes_are_raw_integers(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.py").write_bytes(b"12345")
            code, out = self._run(tmp)
            self.assertEqual(code, 0)
            for line in out.splitlines()[2:]:
                fields = line.split()
                self.assertTrue(fields[2].isdigit())


if __name__ == "__main__":
    unittest.main()
```

## 文件: tests/test_scanner.py
```
"""scanner 核心逻辑单元测试。"""
import tempfile
import unittest
from pathlib import Path

from extstats.scanner import (
    ExtensionStat,
    get_extension,
    scan_directory,
    sort_stats,
)


class TestGetExtension(unittest.TestCase):
    def test_regular_extension(self):
        self.assertEqual(get_extension(Path("foo.py")), ".py")

    def test_no_extension(self):
        self.assertEqual(get_extension(Path("README")), "(none)")
        self.assertEqual(get_extension(Path("Makefile")), "(none)")

    def test_hidden_file_no_extension(self):
        self.assertEqual(get_extension(Path(".gitignore")), "(none)")

    def test_compound_extension(self):
        self.assertEqual(get_extension(Path("backup.tar.gz")), ".gz")

    def test_case_insensitive(self):
        self.assertEqual(get_extension(Path("PHOTO.JPG")), ".jpg")
        self.assertEqual(get_extension(Path("photo.jpg")), ".jpg")


class TestScanDirectory(unittest.TestCase):
    def _make_tree(self, root: Path) -> None:
        (root / "a.py").write_bytes(b"1234567890")      # 10 bytes
        (root / "b.py").write_bytes(b"x" * 20)          # 20 bytes
        (root / "readme").write_bytes(b"12345")         # 5 bytes, (none)
        (root / "image.JPG").write_bytes(b"y" * 30)     # 30 bytes -> .jpg
        sub = root / "sub"
        sub.mkdir()
        (sub / "c.py").write_bytes(b"z" * 40)           # 40 bytes
        (sub / "data.txt").write_bytes(b"w" * 50)       # 50 bytes

    def test_scan_directory_recursive(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._make_tree(Path(tmp))
            stats = scan_directory(Path(tmp))
            self.assertEqual(stats[".py"].count, 3)
            self.assertEqual(stats[".py"].size, 70)
            self.assertEqual(stats["(none)"].count, 1)
            self.assertEqual(stats[".jpg"].count, 1)
            self.assertEqual(stats[".txt"].count, 1)
            self.assertEqual(stats[".txt"].size, 50)


class TestSortStats(unittest.TestCase):
    def _sample(self):
        return {
            ".md": ExtensionStat(count=8, size=100),
            ".py": ExtensionStat(count=10, size=50),
            ".txt": ExtensionStat(count=5, size=200),
        }

    def test_sort_by_count(self):
        items = sort_stats(self._sample())
        self.assertEqual([ext for ext, _ in items], [".py", ".md", ".txt"])

    def test_tie_break_by_size(self):
        stats = {
            "a.py": ExtensionStat(count=10, size=30),
            "b.py": ExtensionStat(count=10, size=60),
        }
        items = sort_stats(stats)
        self.assertEqual([ext for ext, _ in items], ["b.py", "a.py"])

    def test_tie_break_by_extension(self):
        stats = {
            "b.py": ExtensionStat(count=10, size=30),
            "a.py": ExtensionStat(count=10, size=30),
        }
        items = sort_stats(stats)
        self.assertEqual([ext for ext, _ in items], ["a.py", "b.py"])

    def test_top_n(self):
        items = sort_stats(self._sample(), top=2)
        self.assertEqual(len(items), 2)

    def test_top_larger_than_result(self):
        items = sort_stats(self._sample(), top=99)
        self.assertEqual(len(items), 3)

    def test_top_zero_raises(self):
        with self.assertRaises(ValueError):
            sort_stats(self._sample(), top=0)

    def test_top_negative_raises(self):
        with self.assertRaises(ValueError):
            sort_stats(self._sample(), top=-1)

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            stats = scan_directory(Path(tmp))
            self.assertEqual(stats, {})

    def test_case_insensitive_cli_merge(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.JPG").write_bytes(b"1")
            (Path(tmp) / "b.jpg").write_bytes(b"2")
            stats = scan_directory(Path(tmp))
            self.assertEqual(stats[".jpg"].count, 2)

    def test_hidden_files_to_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / ".env").write_bytes(b"1")
            (Path(tmp) / ".gitignore").write_bytes(b"2")
            stats = scan_directory(Path(tmp))
            self.assertEqual(stats["(none)"].count, 2)


if __name__ == "__main__":
    unittest.main()
```
