import SwiftUI
import UIKit
import CoreText

/// Indiana palette (provisional, 2026-11-06; Nick decides, playbook/05-naming.md), light only. Loyalties split (IU, Purdue, Notre Dame;
/// the Region leans Chicago), so the colors come from the state flag (state-prompts/INDIANA_PROMPT.md): flag blue #000F5D (17.6:1 on
/// white) for titles, tint and accents; brick red #8E2A1E (white on it 8.6:1) for the hand-checked guide cards; flag gold #D59F0F only
/// as a pin and card fill under blue text (7.2:1; as text on white it's 2.4:1); a deeper brick #6E1F15 for honors chips; corn-silk cream
/// #F6F1E3 pages. The names `green`/`gold` are kept from Wisconsin Eats so the shared views read the same; here `green` is flag blue
/// and `gold` is brick red.
enum Theme {
    static let green = Color(hex: 0x000F5D)      // flag blue: titles, tint, primary text accents
    static let green2 = Color(hex: 0x1C2E7A)
    static let gold = Color(hex: 0x8E2A1E)       // brick red: card fills under white text, chips
    static let goldSoft = Color(hex: 0xF2DCD7)   // soft brick
    static let lime = Color(hex: 0xD59F0F)       // flag gold, fills only (hand-checked pins, the title shadow), under blue text
    static let limeSoft = Color(hex: 0xF8E9C2)
    static let sand = Color(hex: 0xF6F1E3)       // the Home background, corn-silk cream
    static let red = Color(hex: 0x6E1F15)        // honors chips, deep brick
    static let sandstone = Color(hex: 0x6E1F15)
    static let teal = Color(hex: 0x24607A)       // lake accent (6.5:1 on white)
    static let ink = Color(hex: 0x1A1A1A)
    static let ink2 = Color(hex: 0x2E3440)
    static let muted = Color(hex: 0x5B6270)
    static let surface = Color.white
    static let surface2 = Color(hex: 0xEFE9DA)
    static let surface3 = Color(hex: 0xE3DCCB)
    static let rule = Color(hex: 0xE3DCCB)
    static let rule2 = Color(hex: 0xCAC0AB)
}

extension Color {
    init(hex: UInt32) {
        self.init(red: Double((hex >> 16) & 0xFF) / 255, green: Double((hex >> 8) & 0xFF) / 255, blue: Double(hex & 0xFF) / 255)
    }
}

/// A small uppercase label: "STONE CRAB", "1 MICHELIN STAR".
struct Chip: View {
    enum Style { case gold, green, red, plain, dashed }
    let text: String
    var style: Style = .plain

    var body: some View {
        Text(text.uppercased())
            .font(.caption2.weight(.bold))
            .tracking(0.4)
            .padding(.horizontal, 7).padding(.vertical, 3)
            .foregroundStyle(style == .green || style == .red ? Color.white : style == .dashed ? Theme.muted : style == .gold ? Theme.ink : Theme.green)
            .background {
                RoundedRectangle(cornerRadius: 5).fill(style == .gold ? Theme.goldSoft : style == .green ? Theme.green : style == .red ? Theme.red
                                                       : style == .dashed ? .clear : Theme.surface2)
            }
            .overlay {
                if style == .dashed { RoundedRectangle(cornerRadius: 5).strokeBorder(Theme.rule2, style: StrokeStyle(lineWidth: 1, dash: [3, 2])) }
            }
            .accessibilityLabel(text)
    }
}

/// Indiana Eats' lettering: the system face drawn compressed and heavy for titles and guide names (like a show poster), and the
/// system monospaced face for numbers, dates and small labels. No bundled fonts.
struct DisplayFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .black
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight).width(.compressed))
    }
}

/// Numbers, dates and small labels in the system monospaced face, scaled like DisplayFont.
struct MonoFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .semibold
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight, design: .monospaced))
    }
}

extension View {
    func displayFont(_ size: CGFloat, weight: Font.Weight = .black) -> some View {
        modifier(DisplayFont(size: size, weight: weight))
    }

    func monoFont(_ size: CGFloat, weight: Font.Weight = .semibold) -> some View {
        modifier(MonoFont(size: size, weight: weight))
    }
}

/// The header band: a checkered stripe (two rows of flag-blue and white squares) over a gold baseline. No speedway marks.
struct Stripes: View {
    var height: CGFloat = 6

    var body: some View {
        Canvas { ctx, size in
            let w = size.width, h = size.height, base = h * 0.78, sq = base / 2
            ctx.fill(Path(CGRect(x: 0, y: 0, width: w, height: base)), with: .color(.white))
            var col = 0
            var x: CGFloat = 0
            while x < w {
                for row in 0..<2 where (col + row) % 2 == 0 {
                    ctx.fill(Path(CGRect(x: x, y: CGFloat(row) * sq, width: sq, height: sq)), with: .color(Theme.green))
                }
                x += sq; col += 1
            }
            // the gold baseline last
            ctx.fill(Path(CGRect(x: 0, y: base, width: w, height: h - base)), with: .color(Theme.lime))
        }
        .frame(height: height * 2.4)
        .clipShape(RoundedRectangle(cornerRadius: 3))
        .accessibilityHidden(true)
    }
}

extension View {
    /// An inline navigation title in the display type. UINavigationBar.appearance() didn't reach every SwiftUI bar on iOS 27
    /// (the Map title went from compressed blue to plain black after a push and pop; place titles were always plain), so the
    /// title is our own view in the bar. The navigation title is still set, for the back button and VoiceOver.
    func inlineTitle(_ title: String) -> some View {
        navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(title).displayFont(19, weight: .heavy).foregroundStyle(Theme.green)
                        .lineLimit(1).minimumScaleFactor(0.7)
                        .accessibilityAddTraits(.isHeader)
                }
            }
    }
}
