import SwiftUI

struct AboutView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 8) {
                    Text("INDIANA EATS").displayFont(32).foregroundStyle(Theme.green)
                    Text("A free guide to \(model.restaurantCount.formatted()) Indiana restaurants, led by hand-checked lists of Indiana's own food: breaded pork tenderloins, drive-ins and root beer stands, sugar cream and Hoosier pie, and Amish-country tables, with James Beard honors. No account, no ads, no tracking.")
                        .font(.subheadline).foregroundStyle(Theme.ink2)
                    Text("Indiana Eats is an independent app by Nicholas Soderstrom. It is not affiliated with, endorsed by or operated by the State of Indiana, the Indiana Department of Health or any local health department, the Indiana Alcohol and Tobacco Commission, Visit Indiana or any tourism office, the Indiana Foodways Alliance, Indiana University, Purdue University, the University of Notre Dame, the James Beard Foundation, Apple, or any restaurant or chain. Other names are trademarks of their owners.")
                        .font(.footnote).foregroundStyle(Theme.muted)
                }
                .padding(.vertical, 4)
            }
            Section("How the lists are built") {
                Text("Hand-checked lists (breaded tenderloins, drive-ins and root beer, Hoosier pie, Amish country and the oldest places) include only places checked against a 2025 or 2026 source (a dated story, or an Indiana tourism office's own page for the place), with the address checked. Founding years mean the year it opened at this address.")
                Text("Honors are James Beard Foundation winners, finalists and semifinalists. No MICHELIN Guide covers Indiana.")
                Text("Indiana publishes no statewide open list of its restaurants. This app starts from open map listings (Overture Maps) and keeps the kinds of listing that proved reliable in the states that do publish lists. Whether a place serves alcohol is unknown here, never no. Adult clubs are left out, and stadium, airport and campus stands are hidden with the non-restaurants. Website links are checked, and any that no longer belong to the place are left out.")
                Text("Indiana's 95 local health departments inspect restaurants, and none publishes a grade. Vanderburgh County (weekly) and Porter County (monthly) publish their inspections as reports: places matched to them show each inspection's date and the number of violations the county lists, as published; this app computes no score or grade. Every other place links the state's list of local health departments.")
                Text("Ratings, reviews, hours and photos are Apple Maps' own, shown live in Apple's place card. This app doesn't store or rank by them.")
            }
            .font(.subheadline).foregroundStyle(Theme.ink2)
            Section("Sources") {
                source("Indiana tourism offices", "Visit Indiana, the Elkhart County Convention & Visitors Bureau and Visit Shipshewana pages behind the hand-checked lists, each cited in the data.", "https://visitindiana.in.gov")
                source("Indiana's local health departments", "The state's list of local health departments, each with its own inspection page or contact. Linked from each place.", Links.inspections.absoluteString)
                source("Vanderburgh County Health Department", "Weekly food inspection media reports (restaurants): each inspection's date and number of violations\(model.inspectionsThrough["Vanderburgh County Health Department"].flatMap { DayFormat.text($0) }.map { ", through \($0)" } ?? ""), shown as published and matched to map listings by name and address.", Links.vanderburghReports.absoluteString)
                source("Porter County Health Department", "Monthly food service inspection reports: each inspection's date and number of violations or citations\(model.inspectionsThrough["Porter County Health Department"].flatMap { DayFormat.text($0) }.map { ", through \($0)" } ?? ""), shown as published and matched to map listings by name and address (October 2025's report has no readable text and is left out).", Links.porterReports.absoluteString)
                source("Overture Maps Foundation", "Restaurant listings and websites come from Overture Maps Foundation places data (overturemaps.org)\(model.overtureRelease.map { ", release \($0)" } ?? ""), filtered and reformatted for this app.\n• Data from Meta, Microsoft, DAC and BrightQuery. Available under CDLA Permissive 2.0.\n• Data from Foursquare. \(foursquareCopyright) Available under Apache 2.0. Foursquare data was transformed to the Overture schema; this app further filtered and reformatted it. See the NOTICE below.\n• Data from AllThePlaces. Available under CC0 1.0.\nResearched places are put on the map with Overture Maps addresses data (open address sources under permissive licenses, docs.overturemaps.org/attribution).", "https://overturemaps.org")
                source("Honors", "James Beard Foundation awards are reported as facts and checked by hand against the Foundation's announcements. James Beard Foundation and James Beard Award are trademarks of the James Beard Foundation. Other names belong to their owners.", "https://www.jamesbeard.org/awards")
                source("Maps", "Maps, place cards and directions by Apple Maps.", nil)
            }
            Section("Licenses") {
                NavigationLink("Community Data License Agreement – Permissive 2.0") { LicenseText(file: "CDLA-Permissive-2.0", title: "CDLA Permissive 2.0") }
                NavigationLink("Apache License 2.0") { LicenseText(file: "Apache-2.0", title: "Apache License 2.0") }
                NavigationLink("Foursquare OS Places NOTICE") { LicenseText(file: "Foursquare-NOTICE", title: "Foursquare NOTICE") }
            }
            Section("Privacy") {
                Text("The app collects nothing. Your location, if you allow it, only sorts lists by distance and shows where you are on the map, on this device. Saved places stay on this device.")
                    .font(.subheadline).foregroundStyle(Theme.ink2)
                DataUpdatesNote()
                    .font(.footnote).foregroundStyle(Theme.muted)
                Link("Privacy policy", destination: Links.privacy)
                Link("Terms of use", destination: Links.terms)
            }
            Section("Help") {
                Link("Report a missing or closed place", destination: Links.correctionEmail)
                Link("Email \(Links.supportEmail)", destination: URL(string: "mailto:\(Links.supportEmail)")!)
                Link("Website", destination: Links.site)
                Text("Data as of \(DayFormat.text(model.generated) ?? model.generated). Places open and close; check before you go. Version \(Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "1.0")")
                    .font(.footnote).foregroundStyle(Theme.muted)
            }
        }
        .navigationTitle("About")
        .tint(Theme.green)
    }

    /// the copyright line exactly as the bundled Foursquare NOTICE has it, so the two can't disagree
    private var foursquareCopyright: String {
        guard let url = Bundle.main.url(forResource: "Foursquare-NOTICE", withExtension: "txt"),
              let text = try? String(contentsOf: url, encoding: .utf8),
              let line = text.split(separator: "\n").first(where: { $0.hasPrefix("©") }) else { return "© Foursquare Labs, Inc. All rights reserved." }
        return line.trimmingCharacters(in: .whitespaces)
    }

    @ViewBuilder
    private func source(_ name: String, _ detail: String, _ url: String?) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            if let url, let u = URL(string: url) { Link(name, destination: u).font(.subheadline.weight(.semibold)) }
            else { Text(name).font(.subheadline.weight(.semibold)) }
            Text(detail).font(.caption).foregroundStyle(Theme.muted)
        }
    }
}

/// A bundled license text (Resources/Licenses), reflowed rather than shown as raw 80-column lines.
struct LicenseText: View {
    let file: String
    let title: String

    var body: some View {
        ScrollView {
            Text(text).font(.footnote).foregroundStyle(Theme.ink).textSelection(.enabled)
                .frame(maxWidth: .infinity, alignment: .leading).padding()
        }
        .inlineTitle(title)
    }

    private var text: String {
        guard let url = Bundle.main.url(forResource: file, withExtension: "txt"),
              let raw = try? String(contentsOf: url, encoding: .utf8) else { return "License text missing." }
        // join hard-wrapped lines into paragraphs; keep blank lines and list items as breaks
        var out: [String] = []
        for para in raw.components(separatedBy: "\n\n") {
            let lines = para.components(separatedBy: "\n").map { $0.trimmingCharacters(in: .whitespaces) }
            var joined = ""
            for l in lines where !l.isEmpty {
                let startsItem = l.hasPrefix("–") || l.hasPrefix("-") || l.range(of: #"^\(?[a-z0-9]{1,3}[.)]\s"#, options: .regularExpression) != nil
                joined += joined.isEmpty ? l : (startsItem ? "\n" + l : " " + l)
            }
            if !joined.isEmpty { out.append(joined) }
        }
        return out.joined(separator: "\n\n")
    }
}
