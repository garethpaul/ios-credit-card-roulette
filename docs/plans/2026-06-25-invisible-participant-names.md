# Invisible Participant Names

status: completed

## Context

The shared participant normalizer trims whitespace and rejects empty strings,
but Unicode whitespace, control, or format scalars can still form a nonempty
string that renders as a blank table row and winner label.

## Requirements

- Reject a normalized name when every Unicode scalar is whitespace, control, or
  format.
- Preserve visible names that contain format scalars, including joined emoji.
- Keep both participant entry paths behind the existing shared normalizer.
- Preserve local-only participant state and the no-payment-processing boundary.
- Cover the behavior in XCTest and the portable static baseline.

## Work Completed

- Inspected each normalized name's Unicode scalar general categories and
  required at least one scalar that is neither whitespace, control, nor format.
- Added regression cases for zero-width format characters, a control character,
  whitespace surrounded by format characters, and a visible joined emoji
  family.
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
- Seven isolated hostile mutations were rejected across the scalar guards,
  invisible-name XCTest cases, maintained guidance, plan status, and hosted
  evidence.
- The initial implementation passed hosted macOS `/usr/bin/make test` in
  workflow runs `28163591711` and `28163593617`, including all twenty-eight
  XCTest cases.
- An initial Codex review was clean; a follow-up review identified whitespace
  surrounded by non-trimmed format scalars, the new regression failed before
  the fix, and the final Codex review reported no actionable findings.
- Codex review also independently reproduced the unrelated local Make-path
  failure at the merge-base commit.
