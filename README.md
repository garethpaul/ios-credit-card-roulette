# ios-credit-card-roulette

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/ios-credit-card-roulette` is an Apple platform application or Swift sample. Credit Card Roulette

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: Swift (7).

## Repository Contents

- `CHANGES.md` - concise history of maintenance changes
- `README.md` - project overview and local usage notes
- `CardRoulette` - source or example code
- `CardRoulette.xcodeproj` - Xcode project file
- `CardRouletteTests` - source or example code
- `Makefile` - local verification entry point
- `SECURITY.md` - security reporting and disclosure guidance
- `scripts/check-baseline.py` - static roulette flow and privacy verifier
- `VISION.md` - project direction and maintenance guardrails

Additional scan context:

- Source directories: CardRoulette, CardRouletteTests
- Dependency and build manifests: none detected
- Entry points or build surfaces: `make check`, CardRoulette.xcodeproj
- Test-looking files: CardRouletteTests/CardRouletteTests.swift, CardRouletteTests/Info.plist

## Getting Started

### Prerequisites

- Git
- macOS with Xcode for building Apple platform projects
- Python 3 for local static verification on non-macOS hosts

### Setup

```bash
git clone https://github.com/garethpaul/ios-credit-card-roulette.git
cd ios-credit-card-roulette
make check
```

The checked-in project has no external dependency manifest. Use Xcode for full builds and `make check` for static verification on hosts without Xcode.

## Running or Using the Project

- Open `CardRoulette.xcodeproj` in Xcode, choose the app or sample scheme, and run it on the matching simulator/device.
- The app stores participant names only in memory for the current run.
- The app does not process payments or collect credit card numbers.

## Testing and Verification

Run the local static baseline:

```bash
make check
```

The baseline runs `scripts/check-baseline.py`, parses plist/storyboard/project XML, checks the Swift source inventory, verifies that empty participant lists cannot crash winner selection, checks winner-screen fallback and input guards, checks invalid hex color fallback behavior, and guards against logging, persistence, network reporting, or payment-card handling.

For full legacy verification on macOS, use Xcode's test action or `xcodebuild test` with the appropriate scheme and destination.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- Keep signing files, local xcconfig files, and environment files out of git.

## Security and Privacy Notes

- Review changes touching network requests, sockets, or service endpoints; examples from the scan include CardRoulette/Info.plist, CardRouletteTests/Info.plist.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include CardRoulette/AddParticipantViewController.swift, CardRoulette/Info.plist, CardRoulette/ViewController.swift, CardRoulette/WinnerViewController.swift, and 1 more.
- Participant names and payment choices should remain local-only. Do not add storage, upload, analytics, or real payment processing without a separate privacy and security design.

## Maintenance Notes

- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.
- Run `make check` before pushing changes to Swift sources, plist/storyboard files, Xcode metadata, winner selection, or payment-boundary documentation.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
