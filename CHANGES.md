# Changes

## 2026-06-10

- Added a GitHub Actions workflow that runs the SDK-free `make check` baseline
  for the local-only participant and payment-boundary sample.
- Migrated the app and XCTest source from Swift 2 syntax to Swift 5.
- Raised the deployment target from iOS 8.3 to iOS 12.
- Replaced `arc4random_uniform` with Swift's bounded `Int.random(in:)` API.
- Upgraded Xcode-enabled validation from project parsing to unsigned iOS
  Simulator builds of the app and XCTest targets.
- Guarded winner destination configuration so a storyboard miswire cannot
  force-cast a non-winner controller before assigning winner data.
- Added pinned, read-only macOS CI for the canonical `make check` baseline.
- Made Xcode-enabled checks parse `CardRoulette.xcodeproj` without executing
  gameplay, persisting participant data, or adding payment behavior.

## 2026-06-09

- Added local `make lint`, `make test`, and `make build` gate aliases for the
  static roulette baseline.
- Added a participant removal index guard so stale or invalid table selections
  do not mutate the legacy player list.
- Scoped the card logo to each navigation item title view instead of adding
  navigation-controller overlay subviews.

## 2026-06-08

- Guarded winner selection so an empty participant list shows a fallback instead of dividing by zero.
- Blocked button and shake winner presentation when there are no participants.
- Trimmed participant names before adding them and ignored blank input.
- Moved participant-name normalization into a shared helper and added focused XCTest assertions for it.
- Guarded participant unwind sources before reading participant items.
- Filtered the legacy mutable player list down to typed participant entries before winner selection or row rendering.
- Guarded winner-screen fallback text and trimmed winner-side participant input without force-unwrapping text fields.
- Added bounded local random winner selection.
- Removed table reloads from cell construction.
- Added a fallback cell so participant rows do not force-unwrap a missing storyboard cell.
- Rejected partial invalid hex color scans so malformed colors fall back to gray.
- Added `make check` and a static iOS roulette baseline for plist/storyboard XML, Xcode metadata, source inventory, local-only data flow, and parser guardrails.
- Documented that the app does not collect, store, or process real payment card data.
