# Location-Independent Roulette Verification

status: planned

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

Pending implementation.

## Verification Completed

Pending implementation and validation.

## Risk And Rollback

Verification path resolution only; rollback restores relative recipes.
