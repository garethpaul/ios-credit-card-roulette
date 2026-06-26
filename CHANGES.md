# Changes

## 2026-06-26 11:37 PDT - P1 - Trim invisible participant-name boundaries

### Summary

Removed leading and trailing Unicode whitespace, control, and format scalars
from otherwise visible participant names while preserving internal joiners.

### Work completed

- Replaced whitespace-only trimming with first/last visible Unicode scalar
  boundary selection.
- Removed invisible boundary scalars from otherwise visible participant names.
- Preserved internal format scalars, including zero-width joiners in family
  emoji and format scalars between visible letters.
- Added XCTest regressions for mixed invisible boundaries, wrapped joined emoji,
  and an internal zero-width format scalar.
- Added fail-closed source, test, documentation, and plan contracts.

### Threads

- None; the previous cycle's indexed residual risk reproduced directly through
  the shared normalizer.

### Files changed

- `CardRoulette/ParticipantListItem.swift` — scalar-boundary normalization.
- `CardRouletteTests/CardRouletteTests.swift` — boundary and joiner regressions.
- `scripts/check-baseline.py` — durable implementation and evidence contracts.
- `README.md`, `SECURITY.md`, `VISION.md`, `AGENTS.md` — maintained guidance.
- `docs/plans/2026-06-26-invisible-name-boundaries.md` — completed evidence.
- `CHANGES.md` — this cycle record.

### Validation

- RED `/usr/bin/make check` rejected the old normalizer boundary.
- Swift 5.10 Docker compilation and runtime assertions passed.
- `/usr/bin/make check` passed six Make trust-boundary tests and forty-three project-topology tests; local XCTest skipped truthfully without Xcode.
- Four isolated hostile mutations were rejected for the first boundary, format
  guard, sliced return value, and internal-format regression.
- Gitleaks scanned sixty-seven commits and found no leaks.
- `git diff --check` passed.

### Bugs / findings

- P1 participant identity: names such as zero-width/control-prefixed `Alice`
  rendered like `Alice` but retained hidden boundary scalars in table and winner
  state.

### Blockers

- Native XCTest requires hosted macOS/Xcode; the Linux gate validates the source
  contract and executes the Foundation-only normalizer in Swift 5.10 Docker.

### Next action

- Validate the exact pull-request head with hosted XCTest and CodeQL, then merge
  only if immutable review is clean.

## 2026-06-26 01:36 PDT - P2 - Retire completed roadmap items

### Summary

Reconciled the forward roadmap with participant/winner XCTest coverage, hosted
shared-scheme XCTest, and the existing no-payment guidance.

### Work completed

- Verified twenty-eight focused XCTest cases cover participant validation and
  winner-selection boundaries.
- Verified pinned `macos-15` CI runs the shared-scheme `make test` gate.
- Made the no-payment and no-card-details statement explicit in README guidance.
- Replaced three completed roadmap bullets with an evidence-driven intake rule.

### Threads

- None; repository source, tests, workflow, plans, and guidance were reviewed
  directly.

### Files changed

- `VISION.md` and `README.md` — current evidence and roadmap state.
- `docs/plans/2026-06-26-roadmap-reconciliation.md` — completed decision record.
- `scripts/check-baseline.py` — durable plan and roadmap contracts.
- `CHANGES.md` — this cycle record.

### Validation

- RED static baseline — rejected the missing plan and stale roadmap state.
- `/usr/bin/make check` — passed; local XCTest skipped without `xcodebuild`.
- Six isolated hostile mutations — all rejected.
- Python compilation and `git diff --check` — passed.

### Bugs / findings

- P2 maintenance: all three forward roadmap items had already shipped and could
  prompt duplicate work.

### Blockers

- Local Xcode is unavailable; hosted macOS remains authoritative for XCTest.

### Next action

- Complete exact-head review, hosted macOS XCTest, CodeQL, and merge.

## 2026-06-25 23:32 - P1 - Restore cross-version Make verification

### Summary

Fixed a reproducible Linux baseline failure caused by requiring GNU Make 4.3
to reproduce GNU Make 3.81's pre-load expansion of `$(...)` in an explicit
`-f` path.

### Work completed

- Isolated the safe shell-metacharacter probe from the Make-syntax probe so
  marker evidence cannot leak between cases.
- Bounded the hostile-path contract to the two observed safe interpretations:
  pre-load expansion must fail before repository recipes, while literal-path
  handling must run the repository baseline without executing the marker.
- Made documentation assertions insensitive to Markdown line wrapping.
- Clarified the cross-version-safe invocation in maintainer and security docs.

### Threads

- Started: cross-version Make path diagnosis — direct implementation.
- Continued: continuous open-source maintenance loop.
- Stopped: participant boundary normalization — deferred when the broken main
  verification gate took priority.

### Files changed

- `scripts/test-make-trust-boundary.py` — isolated, version-bounded assertions.
- `README.md`, `SECURITY.md`, `AGENTS.md` — cross-version caller-boundary guidance.
- `docs/plans/2026-06-21-make-trust-boundary.md` — corrected original boundary.
- `docs/plans/2026-06-25-cross-version-makefile-path.md` — completed fix plan.
- `CHANGES.md` — this cycle record.

### Validation

- GNU Make 4.3 mainline harness — reproduced the original hostile-marker failure.
- `python3 scripts/test-make-trust-boundary.py` — 6 tests passed.
- `/usr/bin/make check` and `/usr/bin/make verify` — passed 6 trust-boundary
  tests and 43 project-topology tests; XCTest skipped because Xcode is absent.
- Python compilation, shell syntax, and `git diff --check` — passed.
- Four isolated harness mutations — all rejected.

### Bugs / findings

- P1: The green macOS-oriented contract made the SDK-free Linux baseline fail
  on a valid GNU Make 4.3 literal-path behavior.
- P2: The hostile-path test retained a baseline marker from its preceding probe,
  so it could not independently establish whether repository recipes ran.

### Blockers

- Local Xcode/XCTest execution is unavailable; exact-head hosted macOS remains
  required to exercise GNU Make 3.81, the simulator build, and XCTest.

### Next action

- Open a focused pull request and require hosted macOS/XCTest plus CodeQL before
  exact-head review and merge.

## 2026-06-25

- Rejected participant names made only from Unicode whitespace, control, or
  format scalars while preserving visible joined emoji names.

## 2026-06-21

- Isolated Make verification from caller-selected shell, Python, Xcode, root,
  replacement recipes, and non-executing or error-ignoring modes while
  documenting GNU Make's startup and later double-colon caller boundary.

## 2026-06-19

- Tightened winner and visible-row eligibility to typed participants with
  nonempty normalized names, so blank legacy entries cannot enable selection or
  render as selectable rows.
- Added a `DERIVED_DATA_PATH` override to the XCTest runner and defaulted
  DerivedData to the system temp directory.

## 2026-06-18

- Synchronized winner action availability with typed participant additions,
  initial loading, and removals.

## 2026-06-16

- Added single-flight winner presentation so concurrent button and shake inputs
  cannot queue duplicate winner segues.
- Added visible first-responder ownership to the active roulette screen so
  physical shake input reaches the existing typed winner route.

## 2026-06-14

- Routed shake winner actions from UIKit's authoritative motion argument while
  retaining the typed participant gate.

## 2026-06-13

- Made every Make verification target derive the checkout root so static and
  XCTest gates work from external directories.
- Added a shared typed winner trigger so invalid-only player arrays cannot
  present the winner screen from either the button or shake path.
- Filtered each visible participant row through typed entries so malformed
  legacy values cannot create blank rows or redirect row removal.

## 2026-06-12

- Rejected non-participant objects from participant row removal while preserving
  existing index guards.

## 2026-06-12

- Added a shared Xcode scheme and portable simulator discovery so hosted macOS
  CI executes the existing twelve-case XCTest suite through `make test`.
- Disabled persisted checkout credentials and retained unsigned execution
  without participant upload, payment processing, deployment, or signing.
- Fixed Swift comment stripping so quoted plain-HTTP URLs remain visible to the
  local-only privacy baseline.
- Expanded source guardrails to reject generic payment processors and common
  payment SDK surfaces, not only a specific card-number identifier.

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
