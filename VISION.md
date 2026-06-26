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
- Keep participant-name normalization shared, reject names made only from
  Unicode whitespace, control, or format scalars, trim invisible boundary
  scalars, and preserve internal format scalars in visible joined emoji
- Keep typed and nonempty participant filtering in front of the legacy mutable
  player list
- Keep button and shake navigation behind one typed winner trigger with a
  nonempty-name guard
- Route shake navigation from UIKit's authoritative motion argument while
  retaining the typed participant gate
- Keep visible first-responder ownership scoped to the active roulette screen
  so physical shake delivery matches the documented winner action
- Keep button and shake actions behind single-flight winner presentation so a
  visible round can request only one winner transition
- Keep winner action availability synchronized with typed participant additions
  and removals that leave at least one nonempty normalized name
- Keep each visible participant row mapped to a typed legacy-array entry with a
  nonempty normalized name
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
- Keep pinned GitHub Actions macOS CI executing the shared-scheme XCTest suite
  through the canonical `make test` gate
- Keep participant validation and randomized winner selection covered by the
  focused XCTest suite
- Keep project guidance explicit that the sample does not process payments

Next priorities:

- No unclaimed roadmap item; select future work from reproduced defects,
  platform changes, or reviewed user needs.

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
participant unwind source handling, typed and nonempty participant filtering, participant
removal index guards, winner destination handling, invalid hex fallback
behavior, winner-screen input guards, fallback cell handling, navigation logo
title view ownership, local-only
participant data expectations, project metadata, and documentation guardrails.
The typed winner trigger should use the same nonempty filtered participant
boundary as winner selection before navigation.
On macOS, the baseline should compile the unsigned app and XCTest bundle without
launching gameplay, persisting participants, or introducing payment behavior.

## What We Will Not Merge (For Now)

- Real payment processing
- Storage of credit card data
- Background sharing of participant data
- Broad project migration mixed with app behavior changes

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
