# Participant Removal Index Guard

status: completed

## Context

The participant table removed entries directly from the legacy mutable player
array using the selected row index. Normal table selections are in range, but a
stale or invalid index path should not be able to crash or mutate the list.

## Completed Scope

- Added a `removeParticipantAtIndex` helper that rejects negative and
  out-of-range indexes.
- Routed table-row deletion through the guarded helper before reloading data.
- Added focused XCTest assertions for valid removal and invalid index rejection.
- Extended the static baseline and docs so participant removal remains guarded
  without adding persistence, network, or payment-card handling.

## Verification

- `make check`
- `git diff --check`
