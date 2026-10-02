#!/usr/bin/env python3
"""ChatGPT 浏览器 agent —「ChatGPT 出方案 → DeepSeek 落地 → ChatGPT 复审」工作流的方案/评审角色。

安全模型：与 publish_agent 一致——只驱动用户已登录的 Chrome（CDP 9222），
不保存、不读取任何凭据；自动化只做人类同等的 UI 操作（打开页面、输入、点击、读取），全程可审计。

用法：
  python3 chatgpt_agent.py check                                # 检查 ChatGPT 登录态
  python3 chatgpt_agent.py plan  --task "任务描述" [--out plan.md] [--gpt <id>] [--keep] [--timeout 240]
  python3 chatgpt_agent.py review --task "任务描述" --file 实现摘要.md [--out review.md] [--keep]
  python3 chatgpt_agent.py ask   --prompt "..." [--out reply.md]

前置：Chrome 带 --remote-debugging-port=9222 运行，且 chatgpt.com 已登录（浏览器里人工登录一次即可）。

阶段说明：
  plan   → 让 ChatGPT 输出一份可直接执行的 Markdown 实现方案（阶段 1 产物）
  review → 把 DeepSeek 的实现摘要发给 ChatGPT 复审，输出 Markdown 评审报告（阶段 3 产物）
"""
import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
CDP_URL = "http://127.0.0.1:9222"
LOG_DIR = BASE / "logs"

# ChatGPT Web 关键选择器（2025-08 验证过，若官方改版需同步更新）
SEL = {
    "composer": "#prompt-textarea",                 # 输入框（contenteditable div）
    "send": '[data-testid="send-button"]',          # 发送按钮
}

PLAN_PROMPT = """你是一名资深解决方案架构师。请针对下面的任务，输出一份可直接执行的实现方案。

格式要求（必须遵守）：
- 整个方案放在**单个** ```markdown 代码块内输出，代码块外不要有任何其他文字（不要寒暄、不要"以下是方案"）。
- 方案必须包含以下小节：
  1. 需求理解（一句话）
  2. 技术选型与理由
  3. 实现步骤（编号列表，具体到要创建的文件、每个文件的职责、关键函数/数据结构/接口）
  4. 验收标准（可验证的检查点，供落地后逐条核对）
  5. 风险与注意事项

任务：
{task}"""

REVIEW_PROMPT = """下面是一个任务的实现产物摘要。请以技术评审身份对照任务要求检查这份实现，输出 Markdown 评审报告。

格式要求（必须遵守）：
- 整个报告放在**单个** ```markdown 代码块内输出，代码块外不要有任何其他文字。
- 报告包含：
  1. 总体评价（一句话）
  2. 对照检查：逐条核对任务要点，标注 ✅ 已覆盖 / ⚠️ 部分覆盖 / ❌ 缺失
  3. 问题与缺陷（按严重程度排序，指出具体位置）
  4. 修改建议（按优先级列出，具体可执行）

任务：
{task}

实现产物摘要（可能被截断）：
{content}"""

STREAMING_JS = """() => {
  return [...document.querySelectorAll('button')].some(b => {
    const l = ((b.getAttribute('aria-label') || '') + ' ' + (b.getAttribute('data-testid') || '')).toLowerCase();
    return l.includes('stop') || l.includes('停止');
  });
}"""

# 在页面内把最后一条 assistant 消息的渲染 DOM 重建为 markdown。
# 代码块内容用占位符 \u0000PRE<n>\u0000 表示（其完整值由 Python 端点击"复制"按钮从剪贴板取，
# 因为 ChatGPT 长代码块是 CodeMirror 虚拟化渲染，innerText 只有可视切片）。
ASSEMBLE_JS = """() => {
  const last = [...document.querySelectorAll('[data-message-author-role="assistant"]')].at(-1);
  if (!last) return null;
  const md = last.querySelector('.markdown') || last;
  const pres = [...md.querySelectorAll('pre')];
  let preIndex = 0;
  const inline = (el) => {
    let s = '';
    for (const node of el.childNodes) {
      if (node.nodeType === 3) { s += node.textContent; continue; }
      if (node.nodeType !== 1) continue;
      const t = node.tagName.toLowerCase();
      if (t === 'br') s += '\\n';
      else if (t === 'strong' || t === 'b') s += '**' + inline(node) + '**';
      else if (t === 'em' || t === 'i') s += '*' + inline(node) + '*';
      else if (t === 'code') s += '`' + node.textContent + '`';
      else if (t === 'a') s += '[' + inline(node) + '](' + (node.getAttribute('href') || '') + ')';
      else s += inline(node);
    }
    return s;
  };
  const block = (el) => {
    const t = el.tagName.toLowerCase();
    if (t === 'pre') return '\\u0000PRE' + (preIndex++) + '\\u0000\\n';
    if (t === 'h1' || t === 'h2' || t === 'h3' || t === 'h4') return '\\n' + '#'.repeat(+t[1]) + ' ' + inline(el) + '\\n';
    if (t === 'p') return inline(el) + '\\n';
    if (t === 'blockquote') return '\\n> ' + inline(el).replace(/\\n/g, '\\n> ') + '\\n';
    if (t === 'table') return el.innerText + '\\n';
    if (t === 'ul' || t === 'ol') {
      let n = 0, s = '\\n';
      for (const li of el.children) {
        if (li.tagName.toLowerCase() !== 'li') continue;
        n++;
        const marker = (t === 'ol' ? n + '. ' : '- ');
        const liBlocks = [...li.children].filter(c => ['PRE','P','UL','OL'].includes(c.tagName));
        if (liBlocks.length) {
          let inner = '';
          for (const c of li.children) {
            if (['PRE','P','UL','OL'].includes(c.tagName)) inner += block(c).trim() + '\\n';
            else if (c.nodeType === 1) inner += inline(c);
          }
          s += marker + inner.replace(/\\n+/g, '\\n  ') + '\\n';
        } else {
          s += marker + inline(li).trim() + '\\n';
        }
      }
      return s;
    }
    if (t === 'div') {
      let s = '';
      for (const c of el.children) s += block(c);
      return s;
    }
    return inline(el) + '\\n';
  };
  let mdText = '';
  for (const c of md.children) mdText += block(c);
  // 语言标签只认代码块头部元素（.text-token-text-primary），避免把代码首行误当标签
  const labels = pres.map(pr => {
    const h = pr.querySelector('.text-token-text-primary');
    return (h ? h.innerText : '').trim();
  });
  return {
    mdText,
    nPres: preIndex,
    presVisible: pres.map(pr => pr.innerText || ''),
    presLabels: labels,
  };
}"""

READ_CLIPBOARD_JS = """async () => {
  try { return await navigator.clipboard.readText(); }
  catch (e) { return '__CLIPBOARD_ERROR__ ' + e.message; }
}"""


def log(msg: str, level: str = "INFO") -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {level}: {msg}", flush=True)


def save_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    log(f"已保存 {path}（{len(content)} 字符）")


def connect_browser():
    from playwright.sync_api import sync_playwright
    p = sync_playwright().start()
    try:
        browser = p.chromium.connect_over_cdp(CDP_URL)
    except Exception as exc:
        p.stop()
        log(f"无法连接 {CDP_URL}。请确认 Chrome 已带 --remote-debugging-port=9222 启动。: {exc}", "ERROR")
        sys.exit(2)
    ctx = browser.contexts[0] if browser.contexts else browser.new_context()
    # 提取代码块完整内容需要剪贴板读取权限（仅用于 chatgpt.com）
    try:
        ctx.grant_permissions(["clipboard-read", "clipboard-write"], origin="https://chatgpt.com")
    except Exception:
        pass
    return p, browser, ctx


def new_chatgpt_page(ctx, gpt_id: str = None):
    """新开一个独立标签页到 ChatGPT（新对话），用完即关，不污染用户现有标签页。"""
    page = ctx.new_page()
    url = "https://chatgpt.com/"
    if gpt_id:
        url = f"https://chatgpt.com/g/g-{gpt_id}"
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_selector(SEL["composer"], timeout=30000)
    return page


def type_prompt(page, text: str) -> None:
    """向输入框写入多行文本：优先 execCommand（快且保留换行），失败则逐行键盘输入。"""
    ok = page.evaluate(
        """(t) => {
          const ta = document.querySelector('#prompt-textarea');
          if (!ta) return false;
          ta.focus();
          document.execCommand('insertText', false, t);
          return ta.innerText.trim().length > 0;
        }""",
        text,
    )
    if not ok:
        for i, line in enumerate(text.split("\n")):
            page.keyboard.type(line, delay=3)
            if i < len(text.split("\n")) - 1:
                page.keyboard.press("Shift+Enter")
                time.sleep(0.15)
    time.sleep(0.5)


def send_prompt(page, text: str) -> None:
    type_prompt(page, text)
    btn = page.locator(SEL["send"])
    try:
        if btn.is_visible(timeout=4000) and btn.is_enabled():
            btn.click()
            log("已点击发送按钮")
            return
    except Exception:
        pass
    page.keyboard.press("Enter")  # 兜底：直接回车发送
    log("已回车发送")


def wait_stream_done(page, timeout: int) -> bool:
    """等待流式回复结束：stop 按钮出现后消失（或始终未出现且已有回复）。"""
    deadline = time.time() + timeout
    saw_streaming = False
    while time.time() < deadline:
        streaming = page.evaluate(STREAMING_JS)
        if streaming:
            saw_streaming = True
            time.sleep(1.5)
            continue
        if saw_streaming:
            time.sleep(1.0)  # 落定
            return True
        # 还没出现 streaming：可能还在排队（思考/工具调用前）
        time.sleep(2)
    return False


LABEL_RE = re.compile(r"^(Markdown|Python|Bash|JSON|Text|TOML|运行|复制)$", re.I)


def _strip_label(text: str) -> str:
    """去掉 ChatGPT 代码块渲染时 pre.innerText 首行的语言/按钮标签行。"""
    lines = text.split("\n")
    while lines and LABEL_RE.match(lines[0].strip()):
        lines = lines[1:]
    return "\n".join(lines).strip()


def extract_reply(page) -> dict:
    """把最后一条 assistant 回复从渲染 DOM 重建为 markdown，返回 {text, markdown, source}。

    - 整个回复是一个 ```markdown 代码块（ChatGPT 遵守提示词时）→ 复制按钮直接拿完整源码；
    - 回复是普通 markdown + 多个代码块 → DOM 重建，每个代码块经"复制"按钮取完整内容
      （ChatGPT 长代码块是 CodeMirror 虚拟化渲染，innerText 只有可视切片，必须走剪贴板）。
    """
    data = page.evaluate(ASSEMBLE_JS)
    if not data:
        return {"text": "", "markdown": "", "source": "none"}
    md_text = data["mdText"]
    visible = data["presVisible"]
    labels = data["presLabels"]
    pres = page.locator('[data-message-author-role="assistant"] .markdown pre')
    used_clipboard = 0
    for i in range(data["nPres"]):
        placeholder = f"\u0000PRE{i}\u0000"
        if placeholder not in md_text:
            continue
        value = ""
        try:
            page.bring_to_front()
            page.evaluate("() => document.body.focus()")
            btn = pres.nth(i).locator('button[aria-label="复制"]')
            if btn.count() and btn.first.is_visible(timeout=2000):
                btn.first.click()
                time.sleep(1.0)
                copied = page.evaluate(READ_CLIPBOARD_JS)
                if not copied.startswith("__CLIPBOARD_ERROR__") and copied.strip():
                    value = copied.strip()
                    used_clipboard += 1
        except Exception:
            pass
        if not value:
            value = _strip_label(visible[i] if i < len(visible) else "")
        label = (labels[i] if i < len(labels) else "").strip()
        if label.lower() == "markdown":
            md_text = md_text.replace(placeholder, value)  # 本身就是 markdown 源码
        else:
            fence = "```" + (label if LABEL_RE.match(label) is None else "")
            md_text = md_text.replace(placeholder, f"{fence}\n{value}\n```\n")
    md_text = md_text.replace("\u0000", "").strip()
    if not md_text:
        return {"text": "", "markdown": "", "source": "none"}
    return {
        "text": md_text,
        "markdown": md_text,
        "source": f"dom+clipboard({used_clipboard})",
    }


def wait_reply(page, timeout: int, extra_wait: float = 2.0) -> dict:
    """发送后等待完整回复并提取。带轻量重试。"""
    if not wait_stream_done(page, timeout):
        log("等待回复超时（可能仍在思考）", "WARN")
    reply = extract_reply(page)
    for _ in range(3):
        if reply["markdown"]:
            break
        log("回复为空，重试提取…", "WARN")
        time.sleep(3)
        reply = extract_reply(page)
    return reply


def cmd_check() -> int:
    p, browser, ctx = connect_browser()
    try:
        page = ctx.new_page()
        page.goto("https://chatgpt.com/", wait_until="domcontentloaded", timeout=45000)
        try:
            page.wait_for_selector(SEL["composer"], timeout=20000)
            log("ChatGPT 已登录，输入框可用 ✅")
            return 0
        except Exception:
            log("未找到输入框：可能未登录或出现人机验证，请人工检查浏览器里的 chatgpt.com", "ERROR")
            page.screenshot(path=str(LOG_DIR / "check-fail.png"))
            return 3
        finally:
            page.close()
    finally:
        p.stop()


def cmd_ask(args) -> int:
    p, browser, ctx = connect_browser()
    page = None
    try:
        page = new_chatgpt_page(ctx, args.gpt)
        log(f"新对话已打开: {page.url}")
        send_prompt(page, args.prompt)
        log("已发送，等待回复…")
        reply = wait_reply(page, args.timeout)
        if not reply["markdown"]:
            log("未取到回复内容", "ERROR")
            return 1
        if args.out:
            save_output(Path(args.out), reply["markdown"])
        else:
            print("\n--- ChatGPT 回复 ---\n" + reply["markdown"])
        return 0
    finally:
        if page and not args.keep:
            page.close()
        p.stop()


def cmd_plan(args) -> int:
    prompt = PLAN_PROMPT.format(task=args.task)
    p, browser, ctx = connect_browser()
    page = None
    try:
        page = new_chatgpt_page(ctx, args.gpt)
        log(f"新对话已打开: {page.url}（等待 ChatGPT 出方案）")
        send_prompt(page, prompt)
        log("已发送，等待方案生成…")
        reply = wait_reply(page, args.timeout)
        if not reply["markdown"]:
            log("未取到方案内容", "ERROR")
            return 1
        save_output(Path(args.out), reply["markdown"])
        meta = {
            "task": args.task,
            "generated_at": datetime.now().isoformat(),
            "source": reply["source"],
            "chat_url": page.url,
            "prompt": prompt,
        }
        meta_path = Path(args.out).with_suffix(".meta.json")
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        log(f"元数据已保存 {meta_path}")
        log("阶段1 完成：方案已产出，交给 DeepSeek 落地（见 README 阶段2）。")
        return 0
    finally:
        if page and not args.keep:
            page.close()
        p.stop()


def cmd_review(args) -> int:
    content = Path(args.file).read_text(encoding="utf-8")
    if len(content) > 20000:
        content = content[:20000] + "\n…（摘要过长已截断）"
    prompt = REVIEW_PROMPT.format(task=args.task, content=content)
    p, browser, ctx = connect_browser()
    page = None
    try:
        page = new_chatgpt_page(ctx, args.gpt)
        log(f"新对话已打开: {page.url}（等待 ChatGPT 复审）")
        send_prompt(page, prompt)
        log("已发送，等待评审报告…")
        reply = wait_reply(page, args.timeout)
        if not reply["markdown"]:
            log("未取到评审报告", "ERROR")
            return 1
        save_output(Path(args.out), reply["markdown"])
        log("阶段3 完成：评审报告已产出。若报告中有修改建议，由 DeepSeek 继续修复。")
        return 0
    finally:
        if page and not args.keep:
            page.close()
        p.stop()


def main() -> int:
    parser = argparse.ArgumentParser(description="ChatGPT 浏览器 agent（方案 / 评审角色）")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="检查 ChatGPT 登录态")

    ap = sub.add_parser("ask", help="通用对话（一次性）")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--gpt", default=None)
    ap.add_argument("--timeout", type=int, default=240)
    ap.add_argument("--keep", action="store_true", help="完成后保留标签页")

    pp = sub.add_parser("plan", help="ChatGPT 输出实现方案（阶段1）")
    pp.add_argument("--task", required=True, help="任务描述")
    pp.add_argument("--out", default=None, help="方案保存路径（默认 tasks/<task-id>/plan.md）")
    pp.add_argument("--gpt", default=None, help="指定自定义 GPT 的 id（如 6a29f6ee...）")
    pp.add_argument("--timeout", type=int, default=300)
    pp.add_argument("--keep", action="store_true")

    rp = sub.add_parser("review", help="ChatGPT 复审 DeepSeek 实现（阶段3）")
    rp.add_argument("--task", required=True, help="原任务描述")
    rp.add_argument("--file", required=True, help="实现产物摘要文件（会被截断到 20000 字符）")
    rp.add_argument("--out", default=None, help="评审报告保存路径")
    rp.add_argument("--gpt", default=None)
    rp.add_argument("--timeout", type=int, default=300)
    rp.add_argument("--keep", action="store_true")

    args = parser.parse_args()
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    if args.cmd == "check":
        return cmd_check()
    if args.cmd == "ask":
        return cmd_ask(args)
    if args.cmd == "plan":
        if not args.out:
            log("plan 需要 --out 指定方案保存路径", "ERROR")
            return 2
        return cmd_plan(args)
    if args.cmd == "review":
        if not args.out:
            log("review 需要 --out 指定报告保存路径", "ERROR")
            return 2
        return cmd_review(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
