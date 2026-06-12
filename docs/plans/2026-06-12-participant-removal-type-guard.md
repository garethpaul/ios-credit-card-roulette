# Participant Removal Type Guard

status: completed

## Context

Participant lookup and winner selection ignore objects that are not
`ParticipantListItem`, but `removeParticipantAtIndex` removes any in-range
object. Corrupted or legacy array entries can therefore be mutated through a
participant-only action even though the rest of the UI rejects them.

## Work Completed

- Require the indexed object to be a `ParticipantListItem` before removal.
- Preserve existing negative and out-of-range index handling.
- Add XCTest and static coverage proving invalid typed entries remain untouched.

## Verification Completed

- Local `make check`, `make lint`, `make test`, and `make build` passed. The
  local environment did not provide `xcodebuild`, so `make test` completed the
  static baseline and reported that XCTest requires the hosted macOS runner.
- `python3 -m py_compile scripts/check-baseline.py`,
  `sh -n scripts/run-tests.sh`, and `git diff --check` passed.
- Hostile mutations changing the plan status, inserting an unfinished-work
  marker, falsifying a run ID, or removing the participant type predicate were
  rejected by the baseline.
- The implementation push Check run `27394766979` completed successfully for
  commit `73dd879cbcd09553aa11d6f4cc4257b02fc62cea`.
- The implementation pull-request Check run `27394770140` completed
  successfully for commit `73dd879cbcd09553aa11d6f4cc4257b02fc62cea` and
  executed the CardRoulette XCTest suite on hosted macOS.
- The post-merge push Check run `27394960091` completed successfully for
  commit `041c56d77acfd534eab38eda6c9308b01e7582b6`.
- The CodeQL setup run `27402323075` completed successfully for commit
  `041c56d77acfd534eab38eda6c9308b01e7582b6`.
- The removal helper preserves
  `object(at: index) is ParticipantListItem`, and XCTest preserves
  `testRemoveParticipantAtIndexRejectsInvalidEntryType`.
