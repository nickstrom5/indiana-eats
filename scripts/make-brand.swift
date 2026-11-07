// Indiana Eats brand (final: Nick's decision 2026-11-07): the app icon is concept A of
// scripts/icon-concepts.swift, a breaded pork tenderloin sandwich, on the state flag's blue; the shared Eats Ranked icon style,
// state-prompts/ICON-STYLE.md, no backing shape. No team, university or speedway marks, no "IN Indiana" wordplay.
// Usage, from in-eats/: swift scripts/make-brand.swift   -> IndianaEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png,
// docs/ favicons and touch icons, docs/og.png. scripts/make-site.py draws the same mark as its inline SVG: change both together.
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let BLUE: UInt32 = 0x000F5D, BUN: UInt32 = 0xE3B66A, CUTLET: UInt32 = 0xB9772E, LETTUCE: UInt32 = 0x7DB04A
let GOLD: UInt32 = 0xD59F0F

/// A: the tenderloin sandwich. CoreGraphics y-up, s = canvas size. Identical to icon-concepts.swift's concept A.
func tenderloin(_ c: CGContext, _ s: CGFloat) {
    func R(_ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat, _ r: CGFloat) -> CGPath {
        CGPath(roundedRect: CGRect(x: x * s, y: y * s, width: w * s, height: h * s), cornerWidth: r * s, cornerHeight: r * s, transform: nil)
    }
    c.setFillColor(rgb(BUN)); c.addPath(R(0.28, 0.28, 0.44, 0.12, 0.04)); c.fillPath()          // the bottom bun
    c.setFillColor(rgb(LETTUCE)); c.fill(CGRect(x: 0.28 * s, y: 0.40 * s, width: 0.44 * s, height: 0.04 * s))   // the lettuce
    c.setFillColor(rgb(CUTLET)); c.addPath(R(0.145, 0.44, 0.71, 0.16, 0.08)); c.fillPath()      // the cutlet, far wider than the bun
    c.setFillColor(rgb(BUN)); c.addPath(R(0.28, 0.60, 0.44, 0.14, 0.07)); c.fillPath()          // the top bun
}

func render(_ n: Int, _ path: String, background: Bool) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: background ? CGImageAlphaInfo.noneSkipLast.rawValue : CGImageAlphaInfo.premultipliedLast.rawValue)!
    ctx.setShouldAntialias(true)
    if background { ctx.setFillColor(rgb(BLUE)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n)) }
    tenderloin(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
render(1024, "IndianaEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png", background: true)
try? FileManager.default.createDirectory(atPath: "docs", withIntermediateDirectories: true)
for (n, name) in [(512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png"), (32, "favicon-32.png")] {
    render(n, "docs/" + name, background: true)
}

/// The share image (1200 x 630): flag blue, the tenderloin at the left, the name and tagline at the right, and the app's header band
/// along the bottom: a checkered stripe over a gold baseline (Theme.swift's Stripes).
func og(_ path: String) {
    let W = 1200, H = 630
    let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(BLUE)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
    let band: CGFloat = 64, base: CGFloat = 14, sq = (band - base) / 2
    ctx.setFillColor(.white); ctx.fill(CGRect(x: 0, y: base, width: CGFloat(W), height: band - base))
    ctx.setFillColor(rgb(BLUE))
    var col = 0, x: CGFloat = 0
    while x < CGFloat(W) {
        for row in 0..<2 where (col + row) % 2 == 0 { ctx.fill(CGRect(x: x, y: base + CGFloat(row) * sq, width: sq, height: sq)) }
        x += sq; col += 1
    }
    ctx.setFillColor(rgb(GOLD)); ctx.fill(CGRect(x: 0, y: 0, width: CGFloat(W), height: base))
    ctx.saveGState(); ctx.translateBy(x: 30, y: 80); tenderloin(ctx, 540); ctx.restoreGState()
    let ns = NSGraphicsContext(cgContext: ctx, flipped: false)
    NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = ns
    let title = NSFont(name: "AvenirNextCondensed-Heavy", size: 92) ?? NSFont.boldSystemFont(ofSize: 80)
    let sub = NSFont(name: "AvenirNextCondensed-DemiBold", size: 34) ?? NSFont.boldSystemFont(ofSize: 30)
    NSAttributedString(string: "INDIANA", attributes: [.font: title, .foregroundColor: NSColor.white]).draw(at: NSPoint(x: 600, y: 370))
    NSAttributedString(string: "EATS", attributes: [.font: title, .foregroundColor: NSColor.white]).draw(at: NSPoint(x: 600, y: 276))
    NSAttributedString(string: "TENDERLOINS, PIE & DRIVE-INS", attributes: [.font: sub, .foregroundColor: NSColor(srgbRed: 0.835, green: 0.624, blue: 0.059, alpha: 1)]).draw(at: NSPoint(x: 604, y: 226))
    NSGraphicsContext.restoreGraphicsState()
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
og("docs/og.png")
