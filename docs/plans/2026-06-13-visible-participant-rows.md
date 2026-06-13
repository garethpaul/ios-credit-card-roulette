# Visible Participant Rows

status: completed

## Context

Winner eligibility filters the legacy mutable player array to typed
`ParticipantListItem` values, but the table still reports the raw array count.
An invalid legacy entry therefore appears as a blank row and cannot be removed
through the participant-only raw-index guard.

## Requirements

- R1. The table row count must include only typed participant entries.
- R2. Cell configuration must map a visible row to the corresponding typed
  participant even when invalid legacy entries precede it.
- R3. Selecting a visible row must remove that same typed participant from the
  underlying mutable array and preserve unrelated invalid entries.
- R4. Negative and out-of-range visible rows must not read or mutate the array.
- R5. Existing raw-index lookup/removal guards, winner eligibility, random
  selection, unwind handling, and destination fallback must remain unchanged.
- R6. XCTest and the deterministic checker must reject raw row counts, direct
  visible-row use as an array index, invalid-entry removal, and stale evidence.

## Scope Boundaries

- Do not migrate the legacy `NSMutableArray` in this stacked change.
- Do not add persistence, payment handling, analytics, or network behavior.
- Do not change participant name normalization or winner selection semantics.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `python3 -m py_compile scripts/check-baseline.py`
- `sh -n scripts/run-tests.sh`
- Workflow YAML parsing
- `git diff --check`
- Hostile mutations must reject raw row counts, wrong visible-row mapping,
  direct raw removal, missing invalid-entry preservation, stale plan status,
  and missing verification evidence.

## Work Completed

- Added a typed visible-row to raw-array index mapper with negative and
  out-of-range rejection.
- Routed table row count, cell lookup, and selection removal through the typed
  mapping while preserving the established raw-index helpers.
- Added XCTest coverage for invalid-entry filtering, typed removal mapping,
  invalid visible indexes, and preservation of unrelated malformed entries.
- Extended the static checker and repository guidance with the visible-row
  contract and completed evidence requirements.

## Verification Completed

- All four Make gates (`make lint`, `make test`, `make build`, and
  `make check`) passed against the completed implementation.
- `python3 -m py_compile scripts/check-baseline.py`, `sh -n
  scripts/run-tests.sh`, workflow YAML parsing, and `git diff --check` passed.
- A prepared baseline passed and seven hostile mutations were rejected: raw
  table count, untyped mapping, direct raw cell lookup, direct raw selection
  removal, missing invalid-entry preservation, reopened plan status, and
  removed verification evidence.
- `xcodebuild was unavailable` on this Linux host, so the eighteen-test
  simulator suite was not executed locally. Hosted macOS remains responsible
  for executable XCTest evidence.
