import CoreLocation
import Observation
import UIKit

/// "Near me" sorting. Asks for when-in-use permission only when a list is sorted by distance or "My location" is tapped; the location never leaves the device.
@MainActor
@Observable
final class LocationService: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    private(set) var location: CLLocation?
    private(set) var status: CLAuthorizationStatus = .notDetermined
    /// no fix within 12 seconds, or Core Location reported an error
    private(set) var failed = false
    private var timeout: Task<Void, Never>?
    /// when the current request started: a fix from before it is a cached one (from launch, or before a drive) and doesn't count
    private var askedAt = Date.distantPast

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
        status = manager.authorizationStatus
    }

    var isDenied: Bool { status == .denied || status == .restricted }

    /// Every place is in Indiana, so a reader elsewhere (an App Reviewer in California, say) gets told rather than an empty map.
    /// A coarse outline of the state (Idaho's lesson: a bounding box would count Calumet City, Louisville and Cincinnati),
    /// drawn a little outside the line so the river and lake shores count as inside.
    var isOutsideIndiana: Bool {
        guard let c = location?.coordinate else { return false }
        return !IndianaOutline.contains(c)
    }

    /// Once location is off for the app, iOS won't ask again; the app's page in Settings is the only way back.
    static func openSettings() {
        if let url = URL(string: UIApplication.openSettingsURLString) { UIApplication.shared.open(url) }
    }

    func request() {
        switch manager.authorizationStatus {
        case .notDetermined: manager.requestWhenInUseAuthorization()
        case .authorizedWhenInUse, .authorizedAlways: locate()
        default: break
        }
    }

    private func locate() {
        failed = false
        let asked = Date()
        askedAt = asked
        manager.requestLocation()
        timeout?.cancel()
        timeout = Task { [weak self] in
            try? await Task.sleep(for: .seconds(12))
            guard let self, !Task.isCancelled else { return }
            if (self.location?.timestamp ?? .distantPast) < asked { self.failed = true }
        }
    }

    nonisolated func locationManagerDidChangeAuthorization(_ m: CLLocationManager) {
        let s = m.authorizationStatus
        Task { @MainActor in
            self.status = s
            if s == .authorizedWhenInUse || s == .authorizedAlways { self.locate() }
        }
    }

    nonisolated func locationManager(_ m: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let l = locations.last else { return }
        Task { @MainActor in
            // "My location" needs a fresh fix on every tap: a cached one from before the request would put you back where you were
            guard l.timestamp >= self.askedAt.addingTimeInterval(-2) else { return }
            self.location = l; self.failed = false; self.timeout?.cancel()
        }
    }

    nonisolated func locationManager(_ m: CLLocationManager, didFailWithError error: Error) {
        Task { @MainActor in if self.location == nil { self.failed = true } }
    }
}

extension CLLocation {
    /// "0.4 mi", "12 mi", "1,012 mi" (an App Reviewer in California is a thousand miles out)
    func milesText(to other: CLLocation) -> String {
        let mi = distance(from: other) / 1609.344
        return (mi < 10 ? mi.formatted(.number.precision(.fractionLength(1))) : Int(mi.rounded()).formatted()) + " mi"
    }
}

/// A coarse Indiana outline (longitude, latitude), about 400 m outside the Overture land outline but never over a neighbour's land
/// (buffer 0.004°, minus the neighbours buffered 0.0015°, simplify 0.006°). Indianapolis, Hammond, Gary, Michigan City, Fort Wayne,
/// Lawrenceburg, Jeffersonville, Evansville and Mount Vernon are inside; Calumet City, Chicago, Danville and Lawrenceville (Illinois),
/// New Buffalo (Michigan), Cincinnati (Ohio), Louisville and Henderson (Kentucky) are not.
enum IndianaOutline {
    static let rings: [[(Double, Double)]] = [
        [(-88.001, 37.8), (-88.038, 37.811), (-88.068, 37.802), (-88.089, 37.818), (-88.083, 37.829), (-88.045, 37.82),
         (-88.024, 37.833), (-88.064, 37.854), (-88.096, 37.903), (-88.055, 37.89), (-88.013, 37.891), (-88.02, 37.915),
         (-88.068, 37.925), (-88.057, 37.933), (-88.033, 37.925), (-88.035, 37.956), (-88.011, 37.968), (-88.024, 38.008),
         (-88.007, 38.031), (-88.036, 38.034), (-88.041, 38.045), (-87.992, 38.053), (-87.966, 38.066), (-87.955, 38.086),
         (-87.959, 38.101), (-88.007, 38.085), (-88.014, 38.1), (-87.975, 38.108), (-87.966, 38.131), (-87.945, 38.125),
         (-87.909, 38.164), (-87.921, 38.176), (-87.933, 38.158), (-87.937, 38.174), (-87.975, 38.199), (-87.987, 38.256),
         (-87.964, 38.233), (-87.957, 38.249), (-87.94, 38.257), (-87.951, 38.27), (-87.935, 38.294), (-87.912, 38.299),
         (-87.922, 38.274), (-87.909, 38.267), (-87.872, 38.311), (-87.862, 38.304), (-87.864, 38.277), (-87.841, 38.278),
         (-87.823, 38.344), (-87.806, 38.361), (-87.778, 38.371), (-87.744, 38.41), (-87.74, 38.435), (-87.729, 38.447),
         (-87.754, 38.457), (-87.75, 38.468), (-87.693, 38.487), (-87.672, 38.506), (-87.659, 38.5), (-87.645, 38.507),
         (-87.669, 38.545), (-87.649, 38.556), (-87.638, 38.591), (-87.611, 38.589), (-87.626, 38.606), (-87.614, 38.625),
         (-87.619, 38.639), (-87.593, 38.666), (-87.53, 38.683), (-87.494, 38.741), (-87.503, 38.749), (-87.496, 38.768),
         (-87.513, 38.771), (-87.494, 38.785), (-87.526, 38.819), (-87.526, 38.851), (-87.552, 38.863), (-87.534, 38.878),
         (-87.533, 38.9), (-87.515, 38.903), (-87.526, 38.908), (-87.526, 38.919), (-87.517, 38.923), (-87.52, 38.941),
         (-87.511, 38.955), (-87.529, 38.973), (-87.577, 38.989), (-87.559, 38.992), (-87.578, 39.002), (-87.568, 39.019),
         (-87.579, 39.041), (-87.571, 39.058), (-87.596, 39.081), (-87.619, 39.087), (-87.615, 39.105), (-87.652, 39.108),
         (-87.634, 39.122), (-87.657, 39.136), (-87.642, 39.156), (-87.627, 39.154), (-87.639, 39.166), (-87.619, 39.17),
         (-87.619, 39.184), (-87.588, 39.197), (-87.573, 39.218), (-87.578, 39.243), (-87.57, 39.253), (-87.593, 39.25),
         (-87.609, 39.282), (-87.597, 39.3), (-87.619, 39.306), (-87.605, 39.31), (-87.584, 39.336), (-87.554, 39.339),
         (-87.544, 39.351), (-87.53, 39.348), (-87.522, 41.759), (-84.807, 41.759), (-84.805, 40.31), (-84.821, 39.106),
         (-84.899, 39.055), (-84.832, 38.973), (-84.835, 38.96), (-84.878, 38.922), (-84.878, 38.908), (-84.867, 38.897),
         (-84.814, 38.894), (-84.787, 38.88), (-84.792, 38.862), (-84.831, 38.831), (-84.815, 38.786), (-84.887, 38.796),
         (-84.941, 38.777), (-84.993, 38.78), (-85.173, 38.69), (-85.214, 38.698), (-85.246, 38.733), (-85.276, 38.743),
         (-85.364, 38.732), (-85.415, 38.738), (-85.437, 38.73), (-85.458, 38.688), (-85.44, 38.658), (-85.44, 38.604),
         (-85.417, 38.563), (-85.421, 38.536), (-85.468, 38.511), (-85.5, 38.469), (-85.608, 38.44), (-85.633, 38.399),
         (-85.653, 38.331), (-85.68, 38.299), (-85.742, 38.269), (-85.781, 38.29), (-85.83, 38.278), (-85.844, 38.233),
         (-85.886, 38.2), (-85.908, 38.168), (-85.907, 38.09), (-85.926, 38.023), (-85.947, 38.007), (-86.029, 37.995),
         (-86.04, 37.961), (-86.094, 38.01), (-86.123, 38.017), (-86.179, 38.013), (-86.26, 38.054), (-86.277, 38.089),
         (-86.271, 38.139), (-86.287, 38.159), (-86.361, 38.198), (-86.377, 38.188), (-86.375, 38.167), (-86.328, 38.155),
         (-86.325, 38.14), (-86.336, 38.131), (-86.38, 38.131), (-86.402, 38.107), (-86.431, 38.128), (-86.464, 38.121),
         (-86.465, 38.1), (-86.434, 38.085), (-86.434, 38.068), (-86.453, 38.052), (-86.523, 38.039), (-86.527, 37.968),
         (-86.508, 37.931), (-86.534, 37.919), (-86.589, 37.922), (-86.601, 37.907), (-86.599, 37.868), (-86.639, 37.844),
         (-86.657, 37.845), (-86.661, 37.857), (-86.643, 37.894), (-86.646, 37.91), (-86.681, 37.916), (-86.731, 37.896),
         (-86.764, 37.933), (-86.794, 37.99), (-86.82, 38.001), (-86.857, 37.989), (-86.92, 37.938), (-86.969, 37.934),
         (-87.034, 37.908), (-87.046, 37.894), (-87.045, 37.871), (-87.069, 37.807), (-87.106, 37.785), (-87.13, 37.789),
         (-87.162, 37.841), (-87.22, 37.851), (-87.386, 37.939), (-87.45, 37.943), (-87.51, 37.908), (-87.56, 37.933),
         (-87.575, 37.97), (-87.59, 37.977), (-87.603, 37.972), (-87.607, 37.95), (-87.629, 37.926), (-87.621, 37.906),
         (-87.585, 37.878), (-87.616, 37.833), (-87.653, 37.828), (-87.677, 37.835), (-87.68, 37.856), (-87.663, 37.887),
         (-87.675, 37.903), (-87.76, 37.893), (-87.792, 37.877), (-87.83, 37.878), (-87.874, 37.924), (-87.895, 37.93),
         (-87.942, 37.885), (-87.938, 37.868), (-87.912, 37.843), (-87.908, 37.808), (-87.935, 37.798), (-87.952, 37.773),
         (-88.001, 37.8)],
        [(-87.538, 38.887), (-87.544, 38.892), (-87.541, 38.895), (-87.538, 38.887)]]

    static func contains(_ c: CLLocationCoordinate2D) -> Bool { rings.contains { contains(c, ring: $0) } }

    /// Ray casting: a point is inside when a ray east of it crosses the outline an odd number of times.
    static func contains(_ c: CLLocationCoordinate2D, ring: [(Double, Double)]) -> Bool {
        var inside = false
        var j = ring.count - 1
        for i in 0..<ring.count {
            let (xi, yi) = ring[i], (xj, yj) = ring[j]
            if (yi > c.latitude) != (yj > c.latitude) && c.longitude < (xj - xi) * (c.latitude - yi) / (yj - yi) + xi { inside.toggle() }
            j = i
        }
        return inside
    }
}
