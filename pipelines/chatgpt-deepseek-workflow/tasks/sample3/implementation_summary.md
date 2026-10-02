# 实现产物清单

````text
index.html
````

## 文件: index.html
````
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>番茄钟</title>
<style>
  :root {
    --bg: #1e1e2e;
    --card: #2a2a3e;
    --text: #e8e8f0;
    --accent: #ff6b6b;
    --track: #3a3a52;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
  }
  .card {
    background: var(--card);
    border-radius: 24px;
    padding: 40px 48px;
    text-align: center;
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
  }
  h1 { font-size: 20px; font-weight: 600; letter-spacing: 4px; opacity: 0.85; margin-bottom: 24px; }
  .ring-wrap { position: relative; width: 260px; height: 260px; margin: 0 auto; }
  svg { transform: rotate(-90deg); }
  .track { stroke: var(--track); }
  .progress {
    stroke: var(--accent);
    stroke-linecap: round;
    transition: stroke-dashoffset 0.4s linear;
  }
  .time {
    position: absolute; inset: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 52px; font-weight: 700; font-variant-numeric: tabular-nums;
  }
  .controls { margin-top: 28px; display: flex; gap: 14px; justify-content: center; }
  button {
    border: none; border-radius: 12px;
    padding: 12px 26px; font-size: 16px; cursor: pointer;
    background: var(--accent); color: #fff; transition: transform .1s, opacity .2s;
  }
  button:hover { transform: translateY(-1px); }
  button:active { transform: translateY(0); }
  button.secondary { background: var(--track); }
  .status { margin-top: 16px; font-size: 14px; opacity: 0.6; min-height: 20px; }
  .done .progress { stroke: #4ade80; }
</style>
</head>
<body>
<div class="card">
  <h1>番茄钟</h1>
  <div class="ring-wrap">
    <svg width="260" height="260" viewBox="0 0 260 260">
      <circle class="track" cx="130" cy="130" r="116" fill="none" stroke-width="12"/>
      <circle class="progress" id="progress" cx="130" cy="130" r="116" fill="none"
              stroke-width="12" stroke-dasharray="728.8" stroke-dashoffset="0"/>
    </svg>
    <div class="time" id="time">25:00</div>
  </div>
  <div class="controls">
    <button id="startBtn">开始</button>
    <button id="pauseBtn" class="secondary" disabled>暂停</button>
    <button id="resetBtn" class="secondary">重置</button>
  </div>
  <div class="status" id="status">准备就绪 · 专注 25 分钟</div>
</div>

<script>
(function () {
  "use strict";

  var WORK_MINUTES = 25;
  var TOTAL_MS = WORK_MINUTES * 60 * 1000;
  var CIRCUMFERENCE = 2 * Math.PI * 116; // 与 SVG r=116 一致

  var timeEl = document.getElementById("time");
  var progressEl = document.getElementById("progress");
  var statusEl = document.getElementById("status");
  var startBtn = document.getElementById("startBtn");
  var pauseBtn = document.getElementById("pauseBtn");
  var resetBtn = document.getElementById("resetBtn");
  var card = document.querySelector(".card");

  var state = "idle";        // idle | running | paused
  var remaining = TOTAL_MS;  // 剩余毫秒
  var endAt = 0;             // running 状态下的目标结束时间（Date.now() 基准）
  var timerId = null;

  progressEl.style.strokeDasharray = String(CIRCUMFERENCE);

  function fmt(ms) {
    var totalSec = Math.ceil(ms / 1000);
    var m = Math.floor(totalSec / 60);
    var s = totalSec % 60;
    return (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
  }

  function render() {
    timeEl.textContent = fmt(remaining);
    var ratio = Math.max(0, Math.min(1, remaining / TOTAL_MS));
    progressEl.style.strokeDashoffset = String(CIRCUMFERENCE * (1 - ratio));
  }

  function setButtons() {
    startBtn.disabled = state === "running";
    pauseBtn.disabled = state !== "running";
    resetBtn.disabled = state === "idle" && remaining === TOTAL_MS;
    startBtn.textContent = state === "paused" ? "继续" : "开始";
    pauseBtn.textContent = "暂停";
  }

  function tick() {
    remaining = Math.max(0, endAt - Date.now());
    render();
    if (remaining <= 0) {
      stopTimer();
      state = "idle";
      card.classList.add("done");
      setButtons();
      statusEl.textContent = "时间到！休息一下吧 🍅";
      beep();   // 先响铃：即使弹窗未关闭，声音也立即提醒
      alert("⏰ 时间到！25 分钟专注结束。");
    }
  }

  function stopTimer() {
    if (timerId !== null) {
      clearInterval(timerId);
      timerId = null;
    }
  }

  function beep() {
    try {
      var Ctx = window.AudioContext || window.webkitAudioContext;
      var ctx = window.__pomCtx || (window.__pomCtx = new Ctx());
      // 后台挂起/系统休眠后 AudioContext 可能处于 suspended，先恢复再调度
      if (ctx.state === "suspended") {
        ctx.resume();
      }
      var now = ctx.currentTime;
      [0, 0.35, 0.7].forEach(function (offset) {
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        osc.type = "sine";
        osc.frequency.value = 880;
        gain.gain.setValueAtTime(0.0001, now + offset);
        gain.gain.exponentialRampToValueAtTime(0.5, now + offset + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + offset + 0.25);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now + offset);
        osc.stop(now + offset + 0.3);
      });
    } catch (e) { /* 提示音失败不影响计时 */ }
  }

  startBtn.addEventListener("click", function () {
    if (state === "running") return;
    // 用户手势内初始化音频上下文，满足浏览器自动播放限制
    try {
      var Ctx = window.AudioContext || window.webkitAudioContext;
      if (!window.__pomCtx) window.__pomCtx = new Ctx();
      if (window.__pomCtx.state === "suspended") window.__pomCtx.resume();
    } catch (e) {}
    if (state === "paused" || remaining > 0) {
      endAt = Date.now() + remaining;
    } else {
      remaining = TOTAL_MS;
      endAt = Date.now() + remaining;
    }
    state = "running";
    card.classList.remove("done");
    stopTimer();
    timerId = setInterval(tick, 250);
    statusEl.textContent = "专注中…保持节奏 🍅";
    setButtons();
    render();
  });

  pauseBtn.addEventListener("click", function () {
    if (state !== "running") return;
    remaining = Math.max(0, endAt - Date.now());
    stopTimer();
    state = "paused";
    statusEl.textContent = "已暂停，随时继续";
    setButtons();
    render();
  });

  resetBtn.addEventListener("click", function () {
    stopTimer();
    state = "idle";
    remaining = TOTAL_MS;
    card.classList.remove("done");
    statusEl.textContent = "准备就绪 · 专注 25 分钟";
    setButtons();
    render();
  });

  setButtons();
  render();
})();
</script>
</body>
</html>
````
