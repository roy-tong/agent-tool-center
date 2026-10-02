import CoreGraphics
import Foundation

guard CommandLine.arguments.count >= 4,
      let x = Double(CommandLine.arguments[1]),
      let y = Double(CommandLine.arguments[2]),
      let delta = Int32(CommandLine.arguments[3]) else {
    fputs("Usage: scroll_at x y delta\n", stderr)
    exit(1)
}

let point = CGPoint(x: x, y: y)
let move = CGEvent(mouseEventSource: nil, mouseType: .mouseMoved, mouseCursorPosition: point, mouseButton: .left)
move?.post(tap: .cghidEventTap)

let event = CGEvent(
    scrollWheelEvent2Source: nil,
    units: .line,
    wheelCount: 1,
    wheel1: delta,
    wheel2: 0,
    wheel3: 0
)
event?.post(tap: .cghidEventTap)
