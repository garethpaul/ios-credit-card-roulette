# Navigation Logo Title View

status: completed

## Context

The main, add-participant, and winner screens each created a logo view and added
it directly to the navigation controller's view. Re-entering screens could stack
duplicate overlay subviews outside each controller's normal navigation item
lifecycle.

## Completed Scope

- Scoped each screen's card logo to `navigationItem.titleView`.
- Removed manual navigation-controller overlay insertion and fronting.
- Kept the logo image, size, and tint behavior unchanged.
- Extended the static baseline and docs so the logo stays owned by each
  controller's navigation item title view.

## Verification

- `make check`
- `git diff --check`
