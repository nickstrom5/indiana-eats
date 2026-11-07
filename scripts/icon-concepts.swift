// Indiana Eats icon concepts (2026-11-06), drawn in the shared Eats Ranked style (state-prompts/ICON-STYLE.md): one flat, level,
// centred food on the state flag's blue #000F5D (state-prompts/INDIANA_PROMPT.md), no backing shape, no text or texture, no team or
// speedway marks. Food hexes: bun #E3B66A, breaded cutlet #B9772E, lettuce #7DB04A, crust #C98B3E, sugar cream #F4E2B0,
// corn #F2C230, husk #6E9E3A.
//   A  a breaded pork tenderloin sandwich, front view: the cutlet far wider than the bun
//   B  a slice of sugar cream pie, side view: a level wedge of cream on a crust
//   C  an ear of sweet corn, lying level, with husks at one end
// Usage, from in-eats/: swift scripts/icon-concepts.swift <out dir>   -> concept-{a,b,c}-1024.png
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let BLUE: UInt32 = 0x000F5D, BUN: UInt32 = 0xE3B66A, CUTLET: UInt32 = 0xB9772E, LETTUCE: UInt32 = 0x7DB04A, CRUST: UInt32 = 0xC98B3E
let CREAM: UInt32 = 0xF4E2B0, CORN: UInt32 = 0xF2C230, HUSK: UInt32 = 0x6E9E3A

/// A: the tenderloin sandwich. CoreGraphics y-up, s = canvas size. Identical to make-brand.swift's tenderloin().
func tenderloin(_ c: CGContext, _ s: CGFloat) {
    func R(_ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat, _ r: CGFloat) -> CGPath {
        CGPath(roundedRect: CGRect(x: x * s, y: y * s, width: w * s, height: h * s), cornerWidth: r * s, cornerHeight: r * s, transform: nil)
    }
    c.setFillColor(rgb(BUN)); c.addPath(R(0.28, 0.28, 0.44, 0.12, 0.04)); c.fillPath()          // the bottom bun
    c.setFillColor(rgb(LETTUCE)); c.fill(CGRect(x: 0.28 * s, y: 0.40 * s, width: 0.44 * s, height: 0.04 * s))   // the lettuce
    c.setFillColor(rgb(CUTLET)); c.addPath(R(0.145, 0.44, 0.71, 0.16, 0.08)); c.fillPath()      // the cutlet, far wider than the bun
    c.setFillColor(rgb(BUN)); c.addPath(R(0.28, 0.60, 0.44, 0.14, 0.07)); c.fillPath()          // the top bun
}

/// B: a slice of sugar cream pie from the side: a level crust base, the cream, a crust edge at the back.
func pie(_ c: CGContext, _ s: CGFloat) {
    let w = CGMutablePath()
    w.move(to: CGPoint(x: 0.15 * s, y: 0.36 * s)); w.addLine(to: CGPoint(x: 0.85 * s, y: 0.36 * s))
    w.addLine(to: CGPoint(x: 0.85 * s, y: 0.68 * s)); w.addLine(to: CGPoint(x: 0.15 * s, y: 0.56 * s)); w.closeSubpath()
    c.setFillColor(rgb(CREAM)); c.addPath(w); c.fillPath()
    c.setFillColor(rgb(CRUST)); c.fill(CGRect(x: 0.15 * s, y: 0.30 * s, width: 0.70 * s, height: 0.06 * s))   // the bottom crust
    c.addPath(CGPath(roundedRect: CGRect(x: 0.79 * s, y: 0.30 * s, width: 0.08 * s, height: 0.40 * s), cornerWidth: 0.04 * s, cornerHeight: 0.04 * s, transform: nil)); c.fillPath()   // the rim
}

/// C: an ear of sweet corn, lying level, husks at the left.
func corn(_ c: CGContext, _ s: CGFloat) {
    c.setFillColor(rgb(CORN)); c.fillEllipse(in: CGRect(x: 0.30 * s, y: 0.32 * s, width: 0.56 * s, height: 0.36 * s))
    let h = CGMutablePath()
    h.move(to: CGPoint(x: 0.14 * s, y: 0.50 * s)); h.addLine(to: CGPoint(x: 0.48 * s, y: 0.70 * s)); h.addLine(to: CGPoint(x: 0.40 * s, y: 0.50 * s))
    h.addLine(to: CGPoint(x: 0.48 * s, y: 0.30 * s)); h.closeSubpath()
    c.setFillColor(rgb(HUSK)); c.addPath(h); c.fillPath()
}

func render(_ n: Int, _ path: String, _ draw: (CGContext, CGFloat) -> Void) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(BLUE)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n))
    draw(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
let out = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "playbook/brand"
render(1024, out + "/concept-a-1024.png", tenderloin)
render(1024, out + "/concept-b-1024.png", pie)
render(1024, out + "/concept-c-1024.png", corn)
