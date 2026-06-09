# Changes

## 2026-06-09

- Added a participant removal index guard so stale or invalid table selections
  do not mutate the legacy player list.

## 2026-06-08

- Guarded winner selection so an empty participant list shows a fallback instead of dividing by zero.
- Blocked button and shake winner presentation when there are no participants.
- Trimmed participant names before adding them and ignored blank input.
- Moved participant-name normalization into a shared helper and added focused XCTest assertions for it.
- Guarded participant unwind sources before reading participant items.
- Filtered the legacy mutable player list down to typed participant entries before winner selection or row rendering.
- Guarded winner-screen fallback text and trimmed winner-side participant input without force-unwrapping text fields.
- Switched winner selection to `arc4random_uniform` for bounded local random selection.
- Removed table reloads from cell construction.
- Added a fallback cell so participant rows do not force-unwrap a missing storyboard cell.
- Rejected partial invalid hex color scans so malformed colors fall back to gray.
- Added `make check` and a static iOS roulette baseline for plist/storyboard XML, Xcode metadata, source inventory, local-only data flow, and parser guardrails.
- Documented that the app does not collect, store, or process real payment card data.
