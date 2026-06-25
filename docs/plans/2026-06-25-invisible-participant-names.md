# Invisible Participant Names

status: in progress

## Context

The shared participant normalizer trims whitespace and rejects empty strings,
but Unicode control or format scalars can still form a nonempty string that
renders as a blank table row and winner label.

## Requirements

- Reject a normalized name when every Unicode scalar is a control or format
  scalar.
- Preserve visible names that contain format scalars, including joined emoji.
- Keep both participant entry paths behind the existing shared normalizer.
- Preserve local-only participant state and the no-payment-processing boundary.
- Cover the behavior in XCTest and the portable static baseline.

## Implementation

- Inspect each normalized name's Unicode scalar general categories.
- Require at least one scalar that is neither control nor format.
- Add regression cases for zero-width format characters, a control character,
  and a visible joined emoji family.
- Document the eligibility rule across maintained repository guidance.

## Verification

- Run the focused portable source contract.
- Run `/usr/bin/make check` and `/usr/bin/make test`.
- Run `python3 -m py_compile scripts/check-baseline.py`.
- Run `sh -n scripts/run-tests.sh` and `git diff --check`.
- Run the hosted macOS XCTest workflow when local Xcode is unavailable.
- Run Codex review and resolve actionable findings.
