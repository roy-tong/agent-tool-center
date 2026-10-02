import CoreGraphics
import Foundation

if CommandLine.arguments.count < 3 {
    fputs("usage: click_at x y\n", stderr)
    exit(2)
}

guard let x = Double(CommandLine.arguments[1]), let y = Double(CommandLine.arguments[2]) else {
    fputs("x and y must be numbers\n", stderr)
    exit(2)
}

let point = CGPoint(x: x, y: y)
let down = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown, mouseCursorPosition: point, mouseButton: .left)
let up = CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp, mouseCursorPosition: point, mouseButton: .left)
down?.post(tap: .cghidEventTap)
usleep(80_000)
up?.post(tap: .cghidEventTap)
