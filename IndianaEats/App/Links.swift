import Foundation

/// The app's web pages and support address, in one place.
/// The site is GitHub Pages at the project address until indiana.eatsranked.com resolves (Nick adds a Cloudflare CNAME
/// indiana -> nickstrom5.github.io, DNS only; then scripts/make-site.py sets CUSTOM_DOMAIN). GitHub forwards these github.io
/// links to the custom domain after the switch, so a shipped build keeps working; point them at the new domain in the next update.
enum Links {
    static let site = URL(string: "https://nickstrom5.github.io/indiana-eats/")!
    /// The app's data updates: scripts/publish_app_data.py writes docs/data/app/ (OTA-DATA.md).
    static let appData = URL(string: site.absoluteString + "data/app/")!
    static let privacy = URL(string: site.absoluteString + "privacy.html")!
    static let terms = URL(string: site.absoluteString + "terms.html")!
    /// The Indiana Alcohol and Tobacco Commission: it permits the bars and restaurants that pour alcohol (its permit search isn't used here)
    static let licenses = URL(string: "https://www.in.gov/atc/")!
    /// The state's list of Indiana's local health departments: each county's own inspection page or contact (linked, never read)
    static let inspections = URL(string: "https://www.in.gov/localhealth/")!
    /// the two counties whose published inspection reports are read (Nick's yes, 2026-11-07)
    static let vanderburghReports = URL(string: "https://vanderburghhealth.org/food-inspection-report/")!
    static let porterReports = URL(string: "https://www.in.gov/localhealth/portercounty/food-service-division/food-service-inspections")!
    static func countyReports(_ jurisdiction: String) -> URL? {
        jurisdiction.hasPrefix("Vanderburgh") ? vanderburghReports : jurisdiction.hasPrefix("Porter") ? porterReports : nil
    }
    static let supportEmail = "nick@eatsranked.com"

    static var correctionEmail: URL {
        URL(string: "mailto:\(supportEmail)?subject=Indiana%20Eats%20correction")!
    }

    // MARK: Share

    /// The web app. It opens a place's panel from the hash, explore/#p=<id> (readHash in scripts/explore.js), using the app's ids.
    static let explore = URL(string: site.absoluteString + "explore/")!

    /// What Share sends: the place's own page in the web app, never an Apple Maps or Google link (Apple Maps has its own button).
    /// The id is escaped the way the page's encodeURIComponent would escape it. The web app lists every place
    /// the app does (a unit test checks the ids against docs/data).
    /// The web app lists restaurants only: the venues the app hides by default (stadium stands, gas-station counters) aren't there.
    static func onWeb(_ place: Place) -> Bool { !place.isVenue }
    static func share(_ place: Place) -> URL {
        guard onWeb(place), let id = place.id.addingPercentEncoding(withAllowedCharacters: uriComponent),
              let url = URL(string: explore.absoluteString + "#p=" + id) else { return explore }
        return url
    }

    /// The text that goes with the link: the place, its town and the app. No street address, which Messages turns into a Maps link.
    static func shareMessage(_ place: Place) -> String {
        [place.name, place.city ?? ""].filter { !$0.isEmpty }.joined(separator: ", ") + ", on Indiana Eats"
    }

    /// What encodeURIComponent leaves as is.
    private static let uriComponent = CharacterSet(charactersIn: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.!~*'()")
}
