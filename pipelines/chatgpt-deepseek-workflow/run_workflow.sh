#!/bin/bash
# ============================================================
# 「ChatGPT 出方案 → DeepSeek 落地 → ChatGPT 复审」标准工作流编排
#
# 用法:
#   ./run_workflow.sh <task-id> "<任务描述>"
#
# 流程:
#   阶段1 (plan)     ChatGPT 浏览器 agent 生成实现方案 → tasks/<task-id>/plan.md
#   阶段2 (implement) DeepSeek 编码 agent 读取 plan.md，实现到 tasks/<task-id>/output/
#   阶段3 (review)    ChatGPT 浏览器 agent 复审实现摘要 → tasks/<task-id>/review.md
#
# 阶段2 由 DeepSeek 执行（本仓库配套的 DeepSeek 编码 agent / 本会话），
# 产物放在 tasks/<task-id>/output/ 后，运行 --review 触发阶段3。
# ============================================================
set -euo pipefail
cd "$(dirname "$0")"

TASK_ID="${1:?用法: ./run_workflow.sh <task-id> \"<任务描述>\"}"
TASK="${2:?用法: ./run_workflow.sh <task-id> \"<任务描述>\"}"

TASK_DIR="tasks/${TASK_ID}"
PLAN="${TASK_DIR}/plan.md"
REVIEW="${TASK_DIR}/review.md"
OUT_DIR="${TASK_DIR}/output"

mkdir -p "${OUT_DIR}"

echo "════════════════════════════════════════════"
echo " 工作流: ${TASK_ID}"
echo " 任务 : ${TASK}"
echo "════════════════════════════════════════════"

# ---------- 阶段1: ChatGPT 出方案 ----------
if [[ ! -f "${PLAN}" ]]; then
  echo "▶ 阶段1: ChatGPT 生成方案 → ${PLAN}"
  python3 chatgpt_agent.py plan --task "${TASK}" --out "${PLAN}"
else
  echo "▶ 阶段1: 方案已存在，跳过（${PLAN}）"
fi

# ---------- 阶段2: DeepSeek 落地（人工/agent 执行） ----------
if [[ -z "$(ls -A "${OUT_DIR}" 2>/dev/null)" ]]; then
  echo ""
  echo "▶ 阶段2: 请 DeepSeek 编码 agent 执行以下任务："
  echo "    1. 读取 ${PLAN}"
  echo "    2. 按方案实现，产物写入 ${OUT_DIR}/"
  echo "    3. 完成后运行 ./run_workflow.sh ${TASK_ID} \"${TASK}\" --review 触发复审"
  echo ""
  exit 0
fi

# ---------- 阶段3: ChatGPT 复审 ----------
if [[ "${3:-}" == "--review" ]]; then
  echo "▶ 阶段3: 收集实现摘要 → 提交 ChatGPT 复审"
  SUMMARY="${TASK_DIR}/implementation_summary.md"
  {
    echo "# 实现产物清单"
    echo ""
    echo '````text'
    find "${OUT_DIR}" -type f | sort | sed "s|^${OUT_DIR}/||"
    echo '````'
    while IFS= read -r f; do
      echo ""
      echo "## 文件: ${f#"${OUT_DIR}"/}"
      # 用 4 反引号包裹文件内容，避免文件内出现 ``` 破坏外层 fence
      echo '````'
      cat "${f}"
      echo '````'
    done < <(find "${OUT_DIR}" -type f | sort)
  } > "${SUMMARY}"
  python3 chatgpt_agent.py review --task "${TASK}" --file "${SUMMARY}" --out "${REVIEW}"
  echo ""
  echo "▶ 完成: 评审报告 → ${REVIEW}"
  echo "  若报告含修改建议，由 DeepSeek 修复后重跑 --review。"
fi
