# Completed Roadmap Reconciliation

Status: completed

## Problem

The forward roadmap still asked for participant and winner checks, hosted XCTest
execution, and a no-payment clarification after each item had already shipped.
Leaving completed work listed as future scope invited duplicate maintenance.

## Evidence

- `CardRouletteTests.swift` contains twenty-eight focused tests covering
  participant normalization, eligibility, winner selection and presentation,
  row mapping, removal, unwind, and destination configuration.
- The shared `CardRoulette` scheme includes the test target, and the pinned
  `macos-15` workflow runs the canonical `make test` gate.
- README and security guidance state that the sample does not perform payment
  processing, collect card details, persist participants, or upload them.

## Work Completed

- Moved participant/winner coverage and payment clarity into durable priorities.
- Replaced the completed roadmap bullets with an evidence-driven intake rule.
- Added static contracts so completed items cannot silently return as future work.

## Verification Completed

- RED `python3 scripts/check-baseline.py` rejected the missing plan and all three
  stale roadmap items before documentation was reconciled.
- `make check` passed the static baseline, Make trust boundary, and project
  topology suites; local XCTest skipped because `xcodebuild` is unavailable.
- Six isolated hostile mutations were rejected for a deleted plan, stale
  roadmap bullets, missing intake guidance, stale status, and missing evidence.
- `python3 -m py_compile scripts/check-baseline.py` and `git diff --check` passed.
- README verification confirms the sample does not process payments or accept
  credit card details.
- Hosted `macos-15` remains authoritative for compiling and executing all
  twenty-eight XCTest cases.

## Scope Boundary

- No Swift source, Xcode metadata, workflow, selection behavior, participant
  validation, payment behavior, storage, network, or analytics change is made.
