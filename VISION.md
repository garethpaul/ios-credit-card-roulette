## iOS Credit Card Roulette Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

iOS Credit Card Roulette is a simple Swift app for entering participants and
randomly selecting who pays.

The repository is useful as a small iOS app sample with participant entry,
winner display, and a visual demo. Project context lives in [`README.md`](README.md).

The goal is to keep the app playful, local-first, and easy to build.

The current focus is:

Priority:

- Preserve participant entry and winner-selection flow
- Keep the visual demo and README aligned with app behavior
- Avoid storing real payment information
- Keep participant input trimmed and winner display fallbacks explicit
- Keep participant-name normalization shared and covered by focused tests
- Keep typed participant filtering in front of the legacy mutable player list
- Keep participant removal guarded by row index checks
- Keep winner destination handling guarded before winner data is assigned
- Keep participant table rows resilient with a fallback cell
- Keep the card logo scoped to each navigation item title view
- Maintain a simple Xcode project structure
- Keep `scripts/check-baseline.py` passing for empty-list winner selection,
  local-only participant data, hex color parsing, plist/storyboard XML, and
  Xcode metadata
- Keep `make lint`, `make test`, `make build`, and `make check` available as
  local verification gates
- Keep the app and test targets on Swift 5 with the iOS 12 deployment target
- Keep pinned GitHub Actions macOS CI compiling the unsigned app and XCTest
  bundle through the canonical `make check` gate

Next priorities:

- Add tests or manual checks for participant validation and winner selection
- Add hosted XCTest execution once a shared scheme is maintained
- Clarify that the app does not process payments

Contribution rules:

- One PR = one focused UI, selection, build, or documentation change.
- Verify the app flow after storyboard or controller changes.
- Keep generated signing files and local paths out of git.
- Do not add real payment processing without a separate design.

## Security And Privacy

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

This app should not collect, store, or process credit card numbers. Participant
names or payment choices should remain local unless a future design says
otherwise.

Current baseline: `make lint`, `make test`, `make build`, and `make check` run
`scripts/check-baseline.py` without Xcode. It verifies empty-list winner
selection, shared participant-name normalization, focused XCTest assertions,
participant unwind source handling, typed participant filtering, participant
removal index guards, winner destination handling, invalid hex fallback
behavior, winner-screen input guards, fallback cell handling, navigation logo
title view ownership, local-only
participant data expectations, project metadata, and documentation guardrails.
On macOS, the baseline should compile the unsigned app and XCTest bundle without
launching gameplay, persisting participants, or introducing payment behavior.

## What We Will Not Merge (For Now)

- Real payment processing
- Storage of credit card data
- Background sharing of participant data
- Broad project migration mixed with app behavior changes

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
