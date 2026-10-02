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
