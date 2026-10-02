# sample1 交付裁决记录

- 任务：Python CLI——统计目录内各扩展名文件数量与总大小，`--top N`，递归子目录，无扩展名归 `(none)`
- 产物：`output/`（extstats 包 + tests + pyproject.toml + README.md）
- 流程：ChatGPT 出方案 → DeepSeek 落地 → 自测（27 个单元测试）→ ChatGPT 复审 ×3 轮

## 复审结论

| 轮次 | P0 | P1 | 结论 |
| --- | --- | --- | --- |
| 第 1 轮 | 2（核心源码未出现在摘要中、无测试可见） | 3 | **抓到真实 bug**：摘要生成器只收集顶层文件，`extstats/`、`tests/` 子目录被跳过 |
| 第 2 轮（修复摘要生成器后） | 0 | 3（CLI 端到端断言、os.walk onerror、sort_stats 参数校验） | 可验收，建议补强 |
| 第 3 轮（采纳 P1/P2 后） | 0 | 0 | **通过**（P0 无需修改核心功能） |

## 实际采纳的修改

- 修复 `run_workflow.sh` 摘要生成器：`find -type f` 递归收集所有产物文件 ✅
- `iter_files()` 改用 `os.walk(onerror=...)`，目录遍历错误不再中断整体扫描 ✅
- `sort_stats()` 增加 `top <= 0` 时抛 `ValueError`，与 CLI 语义一致 ✅
- CLI 端到端测试：输出顺序、Bytes 数值、`--top 2` 保留前 2 名、空目录 ✅
- 边界测试：空目录、大小写合并、隐藏文件归 `(none)`、`top=0/-1` 抛错 ✅
- README 补充：符号链接策略、空目录行为 ✅

## 最终裁决

**通过**。27 个单元测试全绿，CLI 实跑验证排序/错误处理正确。
