# Swift 5 App Build

status: completed

## Context

The hosted gate parsed the Xcode project but did not compile it. The app and
tests still used Swift 2-era UIKit, Foundation, segue, table-view, and method
syntax, while the project retained an iOS 8.3 deployment target.

## Completed Scope

- Migrated the app delegate, controllers, participant model, hex parser, and
  XCTest source to Swift 5 syntax.
- Preserved the guarded legacy mutable player array so invalid-entry tests keep
  exercising the participant boundary.
- Replaced `arc4random_uniform` with bounded `Int.random(in:)` winner selection.
- Set app and test target configurations to Swift 5.
- Raised the deployment target from iOS 8.3 to iOS 12.
- Upgraded Xcode-enabled `make check` runs to compile unsigned Debug builds of
  the app and XCTest targets for the iOS Simulator without launching gameplay.
- Extended the baseline and documentation to preserve the toolchain contract.

## Verification

- `python3 scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- hosted macOS simulator build
- `git diff --check`
