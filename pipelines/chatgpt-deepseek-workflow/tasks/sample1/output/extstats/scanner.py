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
