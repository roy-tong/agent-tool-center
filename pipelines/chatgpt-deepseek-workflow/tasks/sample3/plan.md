## 1. 需求理解（一句话）

实现一个**单文件、零外部依赖、可直接双击打开运行**的 `index.html` 番茄钟网页，提供 25 分钟倒计时、开始/暂停/重置、环形进度展示，并在倒计时结束时使用 Web Audio API 合成提示音并弹窗提醒。

## 2. 技术选型与理由

- **HTML5**
  - 页面结构、样式和逻辑全部放入一个 `index.html`。
  - 不引入图片、字体、JavaScript 库或 CSS 框架，满足“单文件、无外部依赖”。

- **原生 CSS**
  - 完成页面布局、按钮状态、响应式适配。
  - 环形进度采用 **SVG + CSS** 实现，避免 Canvas 绘制复杂度，也不依赖外部图标或组件库。

- **SVG `<circle>`**
  - 使用两个同心圆：
    - 背景圆环：固定显示完整轨道。
    - 进度圆环：通过 `stroke-dasharray` 和 `stroke-dashoffset` 控制剩余进度。
  - SVG 相较 `conic-gradient` 更容易精确控制环形进度、线宽和动画。

- **原生 JavaScript**
  - 使用 `performance.now()` / `Date.now()` 计算真实剩余时间，而不是单纯依赖 `setInterval()` 每秒减 1，避免浏览器定时器漂移造成累计误差。
  - `setInterval()` 仅负责周期性刷新 UI。

- **Web Audio API**
  - 使用 `AudioContext + OscillatorNode + GainNode` 在浏览器中实时合成提示音。
  - 不需要 `.mp3`、`.wav` 等外部音频文件。
  - 音频上下文在用户点击“开始”后初始化/恢复，以满足现代浏览器的自动播放限制。

- **浏览器原生 `alert()`**
  - 倒计时结束后弹出明确提示。
  - 无额外 UI 组件依赖，符合最小实现目标。

## 3. 实现步骤

1. **创建项目文件**

   创建：

   ```text
   pomodoro/
   └── index.html
   ```

   `index.html` 同时承担以下职责：

   ```text
   HTML：页面结构
   CSS：页面视觉与环形进度样式
   JavaScript：计时状态机、UI 更新、提示音、结束提醒
   ```

2. **在 `index.html` 中建立基础 HTML 结构**

   推荐结构：

   ```html
   <main class="timer">
     <h1>番茄钟</h1>

     <div class="progress-wrapper">
       <svg class="progress-ring">
         <circle class="progress-ring__background"></circle>
         <circle class="progress-ring__value"></circle>
       </svg>

       <div class="time-display">
         <span id="time">25:00</span>
       </div>
     </div>

     <div class="controls">
       <button id="startPauseBtn">开始</button>
       <button id="resetBtn">重置</button>
     </div>
   </main>
   ```

   关键 DOM ID：

   | ID | 职责 |
   |---|---|
   | `time` | 显示 `MM:SS` |
   | `startPauseBtn` | 开始/暂停切换 |
   | `resetBtn` | 重置倒计时 |

3. **实现页面基础样式**

   在 `<style>` 内定义：

   ```css
   body
   .timer
   .progress-wrapper
   .progress-ring
   .progress-ring__background
   .progress-ring__value
   .time-display
   .controls
   button
   ```

   页面建议：

   - 番茄钟主体水平、垂直居中。
   - 时间数字采用较大的系统字体。
   - 控制按钮至少保证约 `44px` 的点击高度。
   - SVG 环形进度建议尺寸：

   ```text
   viewBox: 0 0 240 240
   圆心: 120,120
   radius: 100
   stroke-width: 10~14
   ```

   不使用外部字体：

   ```css
   font-family:
     -apple-system,
     BlinkMacSystemFont,
     "Segoe UI",
     sans-serif;
   ```

4. **定义计时核心常量和状态**

   `<script>` 中定义：

   ```javascript
   const TOTAL_SECONDS = 25 * 60;

   let remainingSeconds = TOTAL_SECONDS;
   let isRunning = false;
   let timerId = null;
   let endTime = null;
   ```

   职责：

   - `TOTAL_SECONDS`
     - 一个完整番茄周期，固定为 `1500` 秒。
   - `remainingSeconds`
     - 当前剩余秒数。
   - `isRunning`
     - 当前是否正在计时。
   - `timerId`
     - 保存刷新 UI 的定时器 ID。
   - `endTime`
     - 本轮倒计时应该结束的绝对时间戳。

5. **实现时间格式化函数**

   创建：

   ```javascript
   function formatTime(seconds)
   ```

   输入：

   ```text
   1500
   ```

   返回：

   ```text
   25:00
   ```

   实现逻辑：

   ```javascript
   const minutes = Math.floor(seconds / 60);
   const secs = seconds % 60;

   return `${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
   ```

   保证以下结果：

   ```text
   1500 → 25:00
   600  → 10:00
   65   → 01:05
   9    → 00:09
   0    → 00:00
   ```

6. **实现 SVG 环形进度初始化**

   假设 SVG 圆半径：

   ```javascript
   const RADIUS = 100;
   ```

   计算圆周：

   ```javascript
   const CIRCUMFERENCE = 2 * Math.PI * RADIUS;
   ```

   设置：

   ```javascript
   progressCircle.style.strokeDasharray = CIRCUMFERENCE;
   progressCircle.style.strokeDashoffset = 0;
   ```

   为了让进度从 12 点钟方向开始，在 CSS 中设置：

   ```css
   transform: rotate(-90deg);
   transform-origin: 50% 50%;
   ```

7. **实现统一 UI 更新函数**

   创建：

   ```javascript
   function updateDisplay()
   ```

   负责同时更新：

   ```text
   ① 时间文字
   ② 环形进度
   ③ 页面标题（可选但推荐）
   ```

   时间：

   ```javascript
   timeElement.textContent = formatTime(remainingSeconds);
   ```

   进度比例：

   ```javascript
   const progress = remainingSeconds / TOTAL_SECONDS;
   ```

   SVG 偏移量：

   ```javascript
   const offset = CIRCUMFERENCE * (1 - progress);
   ```

   更新：

   ```javascript
   progressCircle.style.strokeDashoffset = offset;
   ```

   因此：

   ```text
   25:00 → 100% 环形进度
   12:30 → 50%
   00:00 → 0%
   ```

   可同时更新浏览器 Tab：

   ```javascript
   document.title = `${formatTime(remainingSeconds)} · 番茄钟`;
   ```

8. **实现开始逻辑**

   创建：

   ```javascript
   function startTimer()
   ```

   执行：

   ```javascript
   isRunning = true;

   endTime = Date.now() + remainingSeconds * 1000;
   ```

   然后启动刷新：

   ```javascript
   timerId = setInterval(tick, 200);
   ```

   推荐 `200~250ms` 刷新一次，而不是严格每 1000ms 刷新一次，以降低事件循环延迟造成的视觉误差。

   同时将按钮文字修改：

   ```text
   开始 → 暂停
   ```

9. **实现核心 `tick()` 函数**

   创建：

   ```javascript
   function tick()
   ```

   不采用：

   ```javascript
   remainingSeconds--;
   ```

   而采用绝对时间计算：

   ```javascript
   const millisecondsLeft = endTime - Date.now();

   remainingSeconds = Math.max(
     0,
     Math.ceil(millisecondsLeft / 1000)
   );
   ```

   然后：

   ```javascript
   updateDisplay();
   ```

   如果：

   ```javascript
   remainingSeconds <= 0
   ```

   调用：

   ```javascript
   finishTimer();
   ```

   这种设计可以降低：

   - 页面卡顿；
   - JavaScript 主线程阻塞；
   - 浏览器后台标签页节流；

   对倒计时准确性的影响。

10. **实现暂停逻辑**

    创建：

    ```javascript
    function pauseTimer()
    ```

    执行：

    ```javascript
    clearInterval(timerId);

    timerId = null;
    isRunning = false;
    ```

    暂停瞬间重新计算剩余时间：

    ```javascript
    remainingSeconds = Math.max(
      0,
      Math.ceil((endTime - Date.now()) / 1000)
    );
    ```

    将按钮文字恢复为：

    ```text
    开始
    ```

    再次点击开始时：

    ```javascript
    endTime = Date.now() + remainingSeconds * 1000;
    ```

    从暂停位置继续。

11. **实现开始/暂停按钮统一入口**

    添加事件：

    ```javascript
    startPauseBtn.addEventListener("click", () => {
      if (isRunning) {
        pauseTimer();
      } else {
        startTimer();
      }
    });
    ```

    状态关系：

    ```text
    未运行
       │
       └─点击开始→ Running
                       │
                       └─点击暂停→ Paused
                                       │
                                       └─点击开始→ Running
    ```

12. **实现重置功能**

    创建：

    ```javascript
    function resetTimer()
    ```

    执行：

    ```javascript
    clearInterval(timerId);

    timerId = null;
    isRunning = false;
    endTime = null;
    remainingSeconds = TOTAL_SECONDS;

    updateDisplay();
    ```

    同时：

    ```javascript
    startPauseBtn.textContent = "开始";
    ```

    不论处于：

    ```text
    初始状态
    正在运行
    暂停状态
    ```

    点击“重置”后都必须立即恢复：

    ```text
    25:00
    ```

13. **实现 Web Audio 初始化**

    定义：

    ```javascript
    let audioContext = null;
    ```

    创建：

    ```javascript
    function ensureAudioContext()
    ```

    内容：

    ```javascript
    if (!audioContext) {
      const AudioContext =
        window.AudioContext || window.webkitAudioContext;

      audioContext = new AudioContext();
    }

    if (audioContext.state === "suspended") {
      audioContext.resume();
    }
    ```

    在用户第一次点击“开始”时调用：

    ```javascript
    ensureAudioContext();
    ```

    这样音频上下文建立在明确的用户交互之后，避免 Chrome、Safari 等浏览器自动播放策略拦截。

14. **实现 Web Audio 合成提示音**

    创建：

    ```javascript
    function playNotificationSound()
    ```

    使用：

    ```javascript
    audioContext.createOscillator();
    audioContext.createGain();
    ```

    推荐生成两到三次短促提示，例如：

    ```text
    880Hz → 0.15s
    660Hz → 0.15s
    880Hz → 0.30s
    ```

    可通过多个 Oscillator：

    ```javascript
    function playTone(frequency, startTime, duration)
    ```

    创建单音。

    `playTone()` 关键步骤：

    ```javascript
    const oscillator = audioContext.createOscillator();
    const gain = audioContext.createGain();

    oscillator.frequency.value = frequency;
    oscillator.type = "sine";

    oscillator.connect(gain);
    gain.connect(audioContext.destination);
    ```

    使用 Gain 淡入淡出，避免波形突然开始/结束产生爆音：

    ```javascript
    gain.gain.setValueAtTime(0, start);
    gain.gain.linearRampToValueAtTime(0.25, start + 0.01);
    gain.gain.linearRampToValueAtTime(0, start + duration);
    ```

15. **实现倒计时结束处理**

    创建：

    ```javascript
    function finishTimer()
    ```

    执行顺序：

    ```javascript
    clearInterval(timerId);

    timerId = null;
    isRunning = false;
    remainingSeconds = 0;

    updateDisplay();

    startPauseBtn.textContent = "开始";

    playNotificationSound();

    alert("时间到！休息一下吧。");
    ```

    为避免同步 `alert()` 可能立即阻塞主线程影响声音启动，可优先执行音频，再略微延迟弹窗：

    ```javascript
    playNotificationSound();

    setTimeout(() => {
      alert("时间到！休息一下吧。");
    }, 100);
    ```

16. **防止倒计时结束事件重复触发**

    `finishTimer()` 被调用后立即：

    ```javascript
    clearInterval(timerId);
    timerId = null;
    isRunning = false;
    ```

    确保后续 `tick()` 不再重复调用：

    ```text
    playNotificationSound()
    alert()
    ```

    必要时增加：

    ```javascript
    let hasFinished = false;
    ```

    开始新周期/重置时：

    ```javascript
    hasFinished = false;
    ```

    完成时：

    ```javascript
    if (hasFinished) return;
    hasFinished = true;
    ```

17. **处理计时结束后的再次启动行为**

    当：

    ```javascript
    remainingSeconds === 0
    ```

    用户再次点击“开始”时，应先恢复一个完整周期：

    ```javascript
    if (remainingSeconds <= 0) {
      remainingSeconds = TOTAL_SECONDS;
    }
    ```

    然后再启动。

    从而支持：

    ```text
    25:00
      ↓
    00:00
      ↓ 时间到
    点击开始
      ↓
    新一轮 25:00
    ```

18. **增加页面不可见情况下的准确性处理**

    由于倒计时基于：

    ```javascript
    endTime - Date.now()
    ```

    即使浏览器后台降低 `setInterval()` 执行频率，也不会造成累计秒数错误。

    推荐补充：

    ```javascript
    document.addEventListener("visibilitychange", () => {
      if (isRunning && !document.hidden) {
        tick();
      }
    });
    ```

    用户重新切回标签页时立即同步剩余时间和环形进度。

19. **增加基本可访问性**

    按钮直接使用原生：

    ```html
    <button>
    ```

    不使用 `<div onclick>` 模拟按钮。

    环形计时区域可增加：

    ```html
    <div
      role="timer"
      aria-live="off"
      aria-label="番茄钟剩余时间"
    >
    ```

    提示结束时使用：

    ```javascript
    alert()
    ```

    提供明确的视觉反馈。

20. **最终文件必须保持完全自包含**

    最终 `index.html` 建议采用：

    ```html
    <!doctype html>
    <html lang="zh-CN">
    <head>
      <meta charset="UTF-8">
      <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
      >
      <title>25:00 · 番茄钟</title>

      <style>
        /* 所有 CSS */
      </style>
    </head>

    <body>
      <!-- 所有 HTML -->

      <script>
        // 所有 JavaScript
      </script>
    </body>
    </html>
    ```

    文件中不得出现：

    ```html
    <link rel="stylesheet" href="...">
    <script src="..."></script>
    <audio src="...">
    <img src="https://...">
    ```

21. **建议最终 JavaScript 函数结构**

    ```javascript
    const TOTAL_SECONDS = 25 * 60;

    function formatTime(seconds) {}
    function updateDisplay() {}

    function ensureAudioContext() {}
    function playTone(frequency, startTime, duration) {}
    function playNotificationSound() {}

    function tick() {}
    function startTimer() {}
    function pauseTimer() {}
    function resetTimer() {}
    function finishTimer() {}

    startPauseBtn.addEventListener("click", ...);
    resetBtn.addEventListener("click", ...);

    document.addEventListener("visibilitychange", ...);

    updateDisplay();
    ```

    核心状态数据：

    ```javascript
    {
      remainingSeconds: number,
      isRunning: boolean,
      timerId: number | null,
      endTime: number | null,
      hasFinished: boolean,
      audioContext: AudioContext | null
    }
    ```

22. **本地运行方式**

    不需要：

    ```text
    npm install
    npm run dev
    Python HTTP Server
    Node.js
    ```

    直接双击：

    ```text
    index.html
    ```

    或拖入 Chrome / Edge / Safari / Firefox 即可运行。

## 4. 验收标准

1. **文件与依赖**
   - [ ] 最终只有一个 `index.html`。
   - [ ] 文件可直接通过 `file://` 打开。
   - [ ] 不依赖 npm、Node.js 或其他运行环境。
   - [ ] 不加载任何 CDN。
   - [ ] 不加载外部 CSS、JavaScript、图片、字体或音频文件。
   - [ ] 断网状态下仍可完整使用。

2. **初始状态**
   - [ ] 页面打开后显示 `25:00`。
   - [ ] 环形进度为完整圆环。
   - [ ] 显示“开始”和“重置”按钮。
   - [ ] 页面刷新后重新回到 `25:00`。

3. **开始**
   - [ ] 点击“开始”后倒计时正常运行。
   - [ ] 按钮文字变成“暂停”。
   - [ ] 时间从 `25:00` 向 `00:00` 递减。
   - [ ] 环形进度随剩余时间同步减少。

4. **暂停**
   - [ ] 运行过程中点击“暂停”后时间停止变化。
   - [ ] 环形进度停止变化。
   - [ ] 按钮文字恢复“开始”。
   - [ ] 暂停 5 秒后重新开始，不会额外扣除暂停期间的 5 秒。

5. **继续**
   - [ ] 暂停后点击“开始”从当前剩余时间继续。
   - [ ] 不会重新跳回 `25:00`。
   - [ ] 连续执行多次开始/暂停不会产生多个定时器同时运行。

6. **重置**
   - [ ] 正在计时时点击“重置”立即停止。
   - [ ] 暂停时点击“重置”立即恢复。
   - [ ] 时间恢复为 `25:00`。
   - [ ] 环形进度恢复完整。
   - [ ] 按钮恢复为“开始”。

7. **环形进度**
   - [ ] `25:00` 时约为 100%。
   - [ ] `12:30` 时约为 50%。
   - [ ] `00:00` 时约为 0%。
   - [ ] 进度方向保持一致。
   - [ ] 环形变化与文字倒计时同步。

8. **倒计时精度**
   - [ ] 不采用单纯 `remainingSeconds--` 作为实际计时依据。
   - [ ] 使用绝对结束时间计算剩余时间。
   - [ ] 页面运行较长时间后不会产生明显累计漂移。
   - [ ] 切换到其他标签页再回来后时间能够正确同步。

9. **倒计时结束**
   - [ ] 最终稳定显示 `00:00`。
   - [ ] 自动停止计时。
   - [ ] 不出现 `-00:01` 等负数。
   - [ ] 播放 Web Audio API 合成的提示音。
   - [ ] 不使用外部音频文件。
   - [ ] 弹出“时间到”类提示。
   - [ ] 每个周期只播放一次提示音。
   - [ ] 每个周期只弹出一次提示框。

10. **下一周期**
    - [ ] 一轮倒计时结束后，再点击“开始”能够启动新的 25 分钟周期。
    - [ ] 新周期环形进度恢复完整。
    - [ ] 新周期能够正常结束并再次提醒。

11. **浏览器兼容**
    - [ ] Chrome 最新稳定版正常工作。
    - [ ] Edge 最新稳定版正常工作。
    - [ ] Firefox 最新稳定版正常工作。
    - [ ] Safari 最新稳定版正常工作。
    - [ ] Web Audio 在用户执行首次交互后可以正常播放。

12. **页面体验**
    - [ ] 桌面端页面布局正常。
    - [ ] 手机浏览器打开后不产生明显横向滚动。
    - [ ] 时间文字清晰可读。
    - [ ] 按钮有明显 hover / active / focus 状态。
    - [ ] 所有核心操作均可通过键盘 Tab + Enter/Space 完成。

## 5. 风险与注意事项

- **浏览器定时器存在漂移**
  - `setInterval(fn, 1000)` 并不保证严格每秒执行。
  - 禁止将“定时器执行次数”直接作为剩余时间依据。
  - 应始终使用：

  ```javascript
  endTime - Date.now()
  ```

  计算实际剩余时间。

- **后台标签页会被浏览器节流**
  - Chrome、Safari 等会降低后台页面 Timer 执行频率。
  - 使用绝对结束时间可以保证用户重新打开页面后恢复正确倒计时。
  - `setInterval()` 只承担 UI 刷新职责。

- **Web Audio 存在自动播放限制**
  - 浏览器通常不允许页面加载后自动创建并播放声音。
  - `AudioContext` 应在“开始”等用户点击事件之后初始化或调用 `resume()`。

- **`alert()` 会阻塞 JavaScript 主线程**
  - 如果先调用 `alert()` 再播放声音，提示音可能被推迟。
  - 建议顺序：

  ```javascript
  playNotificationSound();

  setTimeout(() => {
    alert("时间到！休息一下吧。");
  }, 100);
  ```

- **音频音量不宜过大**
  - `GainNode` 峰值建议控制在约 `0.15~0.3`。
  - 音频开始和结束使用短暂淡入淡出，避免产生 click/pop 爆音。

- **不要使用 CSS transition 对 25 分钟环形进度做单次动画**
  - 浏览器切到后台后可能暂停或改变动画执行行为。
  - 环形状态应始终由当前真实剩余时间计算。

- **必须避免多个定时器并存**
  - `startTimer()` 前应确保当前没有活动 Timer。
  - `pauseTimer()`、`resetTimer()`、`finishTimer()` 都必须执行：

  ```javascript
  clearInterval(timerId);
  timerId = null;
  ```

- **SVG 圆环计算必须统一半径**
  - HTML 中 `<circle r="100">` 与 JavaScript 中 `RADIUS = 100` 必须一致。
  - 否则 `stroke-dashoffset` 会导致进度显示不准确。

- **`Math.ceil()` 与视觉倒计时规则需要保持一致**
  - 剩余 `24:59.2` 应显示 `25:00` 还是 `24:59` 必须采用统一策略。
  - 推荐使用：

  ```javascript
  Math.ceil(millisecondsLeft / 1000)
  ```

  这样开始后的完整第一秒内不会立即从 `25:00` 跳成 `24:59`。

- **单文件约束意味着所有资源必须内嵌**
  - 不使用 favicon 外链。
  - 不使用 Google Fonts。
  - 不使用 Font Awesome。
  - 不使用 Bootstrap/Tailwind CDN。
  - 不使用外部音频。
  - 不使用外部 JavaScript 库。

- **最终实现重点不是复杂框架，而是状态一致性**
  - 整个番茄钟只有几个核心状态：

  ```text
  READY → RUNNING → PAUSED
             │          │
             └──────────┘
             │
             ↓
          FINISHED
             │
             ↓
         NEW CYCLE
  ```

  所有按钮、时间、环形进度和声音提醒都应由同一份计时状态驱动，避免出现“数字已经暂停但圆环仍在变化”或“重置后旧 Timer 继续运行”等状态不同步问题。