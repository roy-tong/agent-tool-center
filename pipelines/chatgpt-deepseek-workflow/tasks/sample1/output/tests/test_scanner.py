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
