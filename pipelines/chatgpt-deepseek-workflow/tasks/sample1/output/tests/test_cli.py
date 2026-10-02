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
