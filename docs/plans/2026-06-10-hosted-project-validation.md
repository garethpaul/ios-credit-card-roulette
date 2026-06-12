# Hosted Project Validation

status: completed

## Context

The static baseline covered participant inputs, winner flow, local-only data,
project metadata, and parser guardrails, but it only printed a reminder when
Xcode was installed. The repository had no current hosted project-file check.

## Completed Scope

- Added a pinned GitHub Actions workflow with read-only repository permissions.
- Runs the canonical `make check` gate on a bounded `macos-15` job.
- Parses `CardRoulette.xcodeproj` whenever Xcode is available.
- Kept gameplay, participant persistence, payment behavior, and signing outside
  hosted CI.
- Extended the checker and documentation to preserve the CI contract.

## Verification

- `python3 scripts/check-baseline.py`
- `make check`
- workflow YAML parse
- `git diff --check`
