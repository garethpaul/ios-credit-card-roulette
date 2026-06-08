## iOS Credit Card Roulette Vision

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
- Maintain a simple Xcode project structure

Next priorities:

- Add README setup and verification instructions
- Add tests or manual checks for participant validation and winner selection
- Modernize Swift/project settings in a dedicated pass
- Clarify that the app does not process payments

Contribution rules:

- One PR = one focused UI, selection, build, or documentation change.
- Verify the app flow after storyboard or controller changes.
- Keep generated signing files and local paths out of git.
- Do not add real payment processing without a separate design.

## Security And Privacy

This app should not collect, store, or process credit card numbers. Participant
names or payment choices should remain local unless a future design says
otherwise.

## What We Will Not Merge (For Now)

- Real payment processing
- Storage of credit card data
- Background sharing of participant data
- Broad project migration mixed with app behavior changes

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
