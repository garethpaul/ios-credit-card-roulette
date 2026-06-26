# Invisible Participant-Name Boundaries

status: completed

## Context

The shared normalizer rejected names made entirely from whitespace, control, or
format scalars, but it returned those scalars unchanged when an otherwise
visible name was wrapped by them. That allowed visually identical participant
names to retain hidden prefixes or suffixes in table and winner state.

## Requirements

- Trim leading and trailing Unicode whitespace, control, and format scalars.
- Reject input with no visible scalar.
- Preserve internal format scalars, including emoji zero-width joiners.
- Keep both participant entry paths, visible-row filtering, and winner
  selection behind the shared normalizer.
- Preserve local-only participant state and the no-payment boundary.

## Work Completed

- Added one visible-scalar predicate shared by both boundary searches.
- Selected the first and last visible Unicode scalar and returned the complete
  range between them.
- Added regressions for mixed invisible boundaries, wrapped family emoji, and
  an internal zero-width format scalar.
- Synchronized maintained guidance and portable fail-closed contracts.

## Verification Completed

- RED `/usr/bin/make check` rejected the missing first/last visible scalar
  boundary.
- Swift 5.10 Docker compilation and runtime assertions passed for invisible
  boundaries, joined emoji, internal format scalars, and invisible-only input.
- `/usr/bin/make check` passed six Make trust-boundary tests and forty-three project-topology tests; Xcode was unavailable locally.
- Four isolated hostile mutations were rejected for the first boundary, format
  guard, sliced return value, and internal-format regression.
- Gitleaks scanned sixty-seven commits and found no leaks.
- `python3 -m py_compile scripts/check-baseline.py scripts/test-project-topology.py scripts/test-make-trust-boundary.py` passed.
- Shell syntax checks and `git diff --check` passed.

## Residual Risk

Native UIKit and XCTest behavior remains hosted-macOS evidence. Unicode
normalization does not perform case folding, canonical composition, uniqueness,
or confusable-character detection.
