# Location-Independent Roulette Verification

status: completed

## Context

Absolute Makefile invocations resolve both the checker and conditional XCTest runner relative to the caller.

## Scope

1. Derive the checkout root from `MAKEFILE_LIST`.
2. Root the Python checker and XCTest runner.
3. Add completed-plan, external-run, guidance, and mutation contracts.
4. Preserve participant, winner-flow, Swift, test, project, and workflow behavior.

## Verification Plan

- Run all four Make gates from the checkout and a temporary directory.
- Run checker compilation, shell syntax, project metadata parsing, and diff checks.
- Reject root, checker, XCTest runner, plan status/evidence, and documentation mutations.
- Inspect intended paths, secrets, and generated artifacts.

## Work Completed

- Derived the checkout root from the loaded Makefile, invoked the checker by
  absolute path, and entered the checkout before running XCTest.
- Added exact Makefile, completed-plan evidence, and synchronized guidance.
- Preserved participant, winner-flow, Swift, test, project, and workflow behavior.

## Verification Completed

- Root and external-directory Make gates passed for all four aliases.
- The root-derivation mutation failed.
- The checker-invocation mutation failed.
- The XCTest-runner mutation failed.
- The plan-status mutation failed.
- The plan-evidence mutation failed.
- The documentation mutation failed.
- Checker compilation, shell syntax, project metadata parsing, diff hygiene,
  intended-path review, secret scanning, and artifact inspection passed.

## Risk And Rollback

Verification path resolution only; rollback restores relative recipes.
