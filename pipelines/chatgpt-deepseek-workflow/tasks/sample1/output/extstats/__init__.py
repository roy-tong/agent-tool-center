"""file-ext-stats 包初始化。"""
from .scanner import ExtensionStat, get_extension, scan_directory, sort_stats

__all__ = ["ExtensionStat", "get_extension", "scan_directory", "sort_stats"]
__version__ = "0.1.0"
