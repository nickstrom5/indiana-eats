import Foundation
import CoreLocation
import UIKit

/// `-screenshot <name>` opens one screen with fixed state for App Store screenshots (scripts/capture-screenshots.sh).
/// Names: home, tenderloin, driveins, pie, amish, honors, oldest, detail, map, saved, about.
enum ScreenshotMode {
    /// Debug builds only: an App Store build ignores the launch argument, so no one can reach seeded screens or fake locations.
    static var name: String? {
        #if DEBUG
        let args = ProcessInfo.processInfo.arguments
        guard let i = args.firstIndex(of: "-screenshot"), i + 1 < args.count else { return nil }
        return args[i + 1]
        #else
        return nil
        #endif
    }
    static var isActive: Bool { name != nil }

    @MainActor
    static func apply(to model: AppModel) {
        guard let name, model.isLoaded else { return }
        model.filters = Filters()
        // downtown Indianapolis (Monument Circle), so "nearest" lists have distances without a permission prompt
        model.screenshotLocation = CLLocation(latitude: 39.7684, longitude: -86.1581)
        // by name and town, ignoring case, so a rebuild with a slightly different casing still finds the place; the hand-checked one first
        let pick = { (n: String, town: String?) -> Place? in
            let hits = model.places.filter { $0.name.caseInsensitiveCompare(n) == .orderedSame && (town == nil || $0.city == town) }
            return hits.first(where: \.handChecked) ?? hits.first
        }
        for p in [pick("Nick's Kitchen", "Huntington"), pick("Triple XXX Family Restaurant", "West Lafayette"), pick("Knickerbocker Saloon", "Lafayette")]
            .compactMap({ $0 }) where !model.isSaved(p) {
            model.toggleSaved(p)
        }
        let open = { (g: Guide) in model.tab = .guides; model.selectedGuide = g; model.guidesPath = [.guide(g)] }
        switch name {
        case "tenderloin": open(.tenderloin)
        case "driveins":
            // West Lafayette, by Triple XXX and the Lafayette Dog n Suds
            model.screenshotLocation = CLLocation(latitude: 40.4259, longitude: -86.9081)
            open(.driveins)
        case "pie": open(.pie)
        case "amish":
            // Shipshewana
            model.screenshotLocation = CLLocation(latitude: 41.6731, longitude: -85.5800)
            open(.amish)
        case "honors": open(.honors)
        case "oldest": open(.oldest)
        case "detail":
            // Triple XXX: Indiana's first drive-in, with its 1929 founding year and its note
            open(.driveins)
            if let p = pick("Triple XXX Family Restaurant", "West Lafayette") ?? model.places.first {
                model.selectedPlace = p; model.guidesPath.append(.place(p))
            }
        case "map": model.tab = .map
        case "saved": model.tab = .saved
        case "about": model.tab = .about
        default: model.tab = .guides; model.selectedGuide = nil
        }
        // iPad shows the place column next to every list, so give each shot a place instead of "Pick a place": a different
        // honored or hand-checked one per shot.
        guard UIDevice.current.userInterfaceIdiom == .pad, model.selectedPlace == nil else { return }
        let place: Place? = switch name {
        case "home": pick("St. Elmo Steak House", "Indianapolis")
        case "tenderloin": pick("Nick's Kitchen", "Huntington")
        case "driveins": pick("Triple XXX Family Restaurant", "West Lafayette")
        case "pie": pick("Clifty Inn", "Madison")
        case "amish": pick("Blue Gate Restaurant & Bakery", "Shipshewana")
        case "map": pick("St. Elmo Steak House", "Indianapolis")
        case "honors": pick("St. Elmo Steak House", "Indianapolis")
        case "oldest": pick("Knickerbocker Saloon", "Lafayette")
        case "saved": pick("Nick's Kitchen", "Huntington")
        case "about": nil
        default: pick("Triple XXX Family Restaurant", "West Lafayette")
        }
        model.selectedPlace = place
    }
}
