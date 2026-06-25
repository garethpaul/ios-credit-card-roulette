# Invisible Participant Names

status: completed

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

## Work Completed

- Inspected each normalized name's Unicode scalar general categories and
  required at least one scalar that is neither control nor format.
- Added regression cases for zero-width format characters, a control character,
  and a visible joined emoji family.
- Documented the eligibility rule across maintained repository guidance and
  added mutation-sensitive portable contracts for source, tests, and docs.

## Verification Completed

- The focused portable source contract failed before implementation and passed
  after the scalar-category guard was added.
- Swift 5.10 Docker compilation and runtime assertions passed for trimmed,
  format-only, control-only, and visible joined-emoji names.
- The portable baseline passed with the unrelated local GNU Make path assertion
  isolated, and all 43 project-topology tests passed.
- `python3 -m py_compile scripts/check-baseline.py`, shell syntax checks, and
  `git diff --check` passed.
- Three isolated hostile mutations were rejected for the format-category guard,
  invisible-name XCTest, and maintained README guidance.
- Hosted macOS `/usr/bin/make test` passed in workflow runs `28163591711` and
  `28163593617`, including all twenty-eight XCTest cases.
- Codex review reported no actionable diff-introduced findings and independently
  reproduced the local Make-path failure at the merge-base commit.
