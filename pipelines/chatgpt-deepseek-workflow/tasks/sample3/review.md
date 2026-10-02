# 技术评审报告

## 1. 总体评价

实现已完整覆盖任务要求，核心计时逻辑、暂停恢复、环形进度、Web Audio 提示音和结束弹窗均可用，整体可直接交付；主要需要补强后台计时结束提醒、音频上下文恢复和少量可维护性/可访问性细节。

## 2. 对照检查

| 任务要点 | 状态 | 检查结果 |
|---|---|---|
| 单个 HTML 文件实现 | ✅ 已覆盖 | 仅包含 `index.html`，CSS 与 JavaScript 均内嵌在文件中。 |
| 无外部依赖 | ✅ 已覆盖 | 未引用 CDN、第三方 JS/CSS、字体或音频资源。 |
| 25 分钟倒计时 | ✅ 已覆盖 | `WORK_MINUTES = 25`，通过 `TOTAL_MS = 25 * 60 * 1000` 初始化倒计时。 |
| 开始按钮 | ✅ 已覆盖 | `startBtn` 可从初始状态启动计时，并在暂停后变为“继续”。 |
| 暂停按钮 | ✅ 已覆盖 | 暂停时根据 `endAt - Date.now()` 保存实际剩余时间，而非单纯依赖 interval 次数，逻辑正确。 |
| 重置按钮 | ✅ 已覆盖 | 可停止计时并恢复至 `25:00`、初始进度及初始状态。 |
| 环形进度显示 | ✅ 已覆盖 | 使用 SVG `circle` 与 `stroke-dashoffset` 根据剩余时间动态更新环形进度。 |
| 倒计时结束播放提示音 | ✅ 已覆盖 | `beep()` 使用 Web Audio API 创建 `OscillatorNode`，连续播放三次 880Hz 提示音。 |
| 无需外部音频文件 | ✅ 已覆盖 | 声音完全由 Web Audio API 实时合成。 |
| 倒计时结束弹出提示 | ✅ 已覆盖 | `tick()` 在剩余时间归零后执行 `alert()`。 |
| 可直接在浏览器打开 | ✅ 已覆盖 | 使用标准 HTML/CSS/JavaScript 与浏览器原生 API，无构建、服务器或模块加载要求。 |
| 浏览器自动播放策略处理 | ✅ 已覆盖 | 首次点击“开始”时在用户手势中创建/恢复 `AudioContext`，明显考虑了 autoplay policy。 |
| 长时间计时准确性 | ✅ 已覆盖 | 使用绝对结束时间 `endAt` 和 `Date.now()` 计算剩余时间，避免 `setInterval` 累积漂移。 |

## 3. 问题与缺陷

### 中等：浏览器进入后台后，“时间到”提醒可能明显延迟

**位置：**

```javascript
timerId = setInterval(tick, 250);
以及：
```JavaScript
function tick() {
  remaining = Math.max(0, endAt - Date.now());
  ...
  if (remaining <= 0) {
    ...
    beep();
    alert(...);
  }
}
```

**问题：**
计时数值本身采用 `endAt - Date.now()`，因此不会因为 `setInterval` 漂移而产生累计误差，这是正确的。
但“完成事件”仍完全依赖 `setInterval` 触发。浏览器标签页进入后台、设备休眠或浏览器实施 Timer Throttling 后，`tick()` 可能无法在 25 分钟结束的准确时刻执行。
因此可能出现：

1. 用户切到其他标签页；
  
2. 实际 25 分钟已经结束；
  
3. 页面逻辑仍没有执行 `beep()` / `alert()`；
  
4. 用户重新打开页面后才触发结束提醒。
  
这不会造成“显示剩余时间错误”，但会影响番茄钟最关键的“到点提醒”体验。


### 中等：`AudioContext.resume()` 为异步操作，但当前代码未等待恢复完成
**位置：**
```JavaScript
if (ctx.state === "suspended") {
  ctx.resume();
}
var now = ctx.currentTime;
```

以及开始按钮：
```JavaScript
if (window.__pomCtx.state === "suspended") window.__pomCtx.resume();
```

**问题：**
`AudioContext.resume()` 返回 Promise。当前实现调用后立即基于 `ctx.currentTime` 调度振荡器。
大多数现代浏览器通常能够正常工作，但从 API 语义来看，并不能保证 `resume()` 已经完成。
尤其经历以下情况后可能出现兼容性问题：

- 系统休眠；
  
- 页面长时间置于后台；
  
- 移动浏览器自动 suspend AudioContext；
  
- 某些更严格的 autoplay policy。
  
结果可能是倒计时结束弹窗正常出现，但提示音没有可靠播放。


### 低：结束状态仍被设置为 `idle`，状态语义不够严谨
**位置：**
```JavaScript
if (remaining <= 0) {
  stopTimer();
  state = "idle";
  card.classList.add("done");
  ...
}
```

**问题：**
代码注释声明：
```JavaScript
var state = "idle"; // idle | running | paused
```

完成后又使用：
```JavaScript
card.classList.add("done");
```

实际上系统已经存在第四种业务状态——`done`，但它仅通过 CSS class 表达，而 JavaScript 状态仍然是 `idle`。
目前功能没有明显错误，但会造成状态模型不一致：

- `idle + remaining=TOTAL_MS`：真正的初始状态；
  
- `idle + remaining=0 + .done`：完成状态。
  
以后增加自动休息、番茄次数统计、重复启动等逻辑时容易产生条件判断复杂化。


### 低：SVG 半径及周长存在重复硬编码
**位置：**
HTML：
```HTML
<circle ... r="116" .../>
```

JavaScript：
```JavaScript
var CIRCUMFERENCE = 2 * Math.PI * 116;
```

以及 HTML 中：
```HTML
stroke-dasharray="728.8"
```

**问题：**
`116` 和对应周长同时存在于 HTML 和 JavaScript 中。
虽然 JavaScript 随后会覆盖：
```JavaScript
progressEl.style.strokeDasharray = String(CIRCUMFERENCE);
```

所以当前不会导致功能错误，但修改 SVG 尺寸时容易遗漏 JavaScript 中的 `116`，导致环形进度计算错误。


### 低：完成后重新“开始”的逻辑依赖 `remaining === 0` 的隐式分支
**位置：**
```JavaScript
if (state === "paused" || remaining > 0) {
  endAt = Date.now() + remaining;
} else {
  remaining = TOTAL_MS;
  endAt = Date.now() + remaining;
}
```

**问题：**
这里实际上承担了三种含义：

- paused → 继续；
  
- idle 且 remaining > 0 → 开始；
  
- idle 且 remaining === 0 → 新一轮开始。
  
逻辑当前正确，但可读性一般，而且与前述缺少 `done` 状态的问题相关。
建议显式表达“新一轮番茄钟”的业务状态，而不是依赖 `remaining > 0` 推断。


### 低：缺少基础可访问性处理
**位置：**
```SVG
SVG
```

以及：
```HTML
<div class="status" id="status">...</div>
```

**问题：**
页面视觉使用没有问题，但可以进一步增加：

- `aria-label`；
  
- `aria-live`；
  
- SVG 的辅助说明；
  
- `:focus-visible` 键盘焦点样式。
  
例如状态文本变化和倒计时结束信息目前不会主动向屏幕阅读器播报。
该项不属于原始任务硬性要求，因此不影响需求验收。

## 4. 修改建议

### P1：提高计时结束提醒的可靠性
保留目前基于 `endAt` 的计时方案，因为这部分设计正确。
建议额外监听页面重新激活：
```JavaScript
document.addEventListener("visibilitychange", function () {
  if (!document.hidden && state === "running") {
    tick();
  }
});

window.addEventListener("focus", function () {
  if (state === "running") {
    tick();
  }
});
```

这样标签页恢复前台时可以立即校正状态并触发完成逻辑。
需要说明：纯前端网页无法完全保证在浏览器后台节流、设备休眠时精确到秒播放声音；这是浏览器运行机制限制，而不是单纯调整 `setInterval` 就能彻底解决的问题。

### P1：正确处理 `AudioContext.resume()` 的异步行为
建议将提示音函数改为异步流程：
```JavaScript
async function beep() {
  try {
    var Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;

    var ctx = window.__pomCtx || (window.__pomCtx = new Ctx());

    if (ctx.state === "suspended") {
      await ctx.resume();
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
  } catch (e) {
    console.warn("提示音播放失败", e);
  }
}
```

如果希望保证“先响铃再弹窗”，完成流程也应考虑 `resume()` 的 Promise，而不是仅从代码执行顺序判断。

### P2：增加显式 `done` 状态
将：
```JavaScript
// idle | running | paused
```

调整为：
```JavaScript
// idle | running | paused | done
```

结束时：
```JavaScript
state = "done";
```

开始逻辑可明确写成：
```JavaScript
if (state === "done") {
  remaining = TOTAL_MS;
}

endAt = Date.now() + remaining;
state = "running";
```

这样业务状态更加清晰，也方便后续扩展：

- 工作/休息循环；
  
- 番茄次数；
  
- 自动开始下一轮；
  
- 完成动画。
  

### P2：从 SVG 本身获取圆周长度，删除魔法数字
可改为：
```JavaScript
var CIRCUMFERENCE = progressEl.getTotalLength();
```

从而删除：
```JavaScript
2 * Math.PI * 116
```

同时 HTML 中无需硬编码：
```HTML
stroke-dasharray="728.8"
```

避免 SVG 尺寸调整后 JavaScript 与 HTML 不同步。

### P3：补充可访问性
例如：
```HTML
<div
  class="time"
  id="time"
  role="timer"
  aria-live="off"
>
  25:00
</div>

<div
  class="status"
  id="status"
  aria-live="polite"
>
  准备就绪 · 专注 25 分钟
</div>
```

并为按钮增加明显的键盘焦点状态：
```CSS
button:focus-visible {
  outline: 3px solid #fff;
  outline-offset: 3px;
}
```


## 结论
该实现不存在阻塞交付的功能缺陷，**任务要求可以判定为全部覆盖并通过验收**。优先建议修复 `AudioContext.resume()` 的异步处理，并加强页面后台/恢复前台后的结束检测；其余问题主要属于代码健壮性、状态建模和工程质量优化。
```

```