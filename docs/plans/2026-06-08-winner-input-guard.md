# Winner Input Guard Plan

status: completed

## Context

`ios-credit-card-roulette` already trims participant names when adding a participant from the main entry flow. `WinnerViewController` still force-unwraps text field contents in its segue handler and can accept whitespace-only input if that path is wired later.

## Objectives

- Show fallback winner text when the winner screen is opened without a winner name.
- Reset winner-side participant output before handling a segue.
- Trim winner-side text field input and ignore blank values.
- Extend the static baseline so the winner controller cannot reintroduce text-field force unwraps.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
