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
