# iOS Credit Card Roulette Baseline Plan

status: completed

## Context

`ios-credit-card-roulette` is a legacy Swift iOS sample for entering local
participants and randomly selecting a winner. This Linux host does not provide
Xcode, so local verification needs a static baseline while full app builds
remain a macOS/Xcode responsibility.

## Objectives

- Prevent empty participant lists from crashing winner selection.
- Prevent winner presentation when there are no participants.
- Trim participant names and ignore blank entries.
- Keep participant names local-only and avoid payment-card data handling.
- Reject invalid partial hex color scans.
- Add a reproducible `make check` baseline for project metadata, plist/storyboard XML, source inventory, and privacy guardrails.
- Document Xcode verification expectations and payment-data boundaries.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
