# Table Cell Fallback Plan

status: completed

## Context

`ViewController.tableView(_:cellForRowAtIndexPath:)` dequeues the participant row cell from the storyboard and force-unwraps the result. A storyboard reuse identifier mismatch would crash while rendering the participant list.

## Objectives

- Provide a default `UITableViewCell` fallback when dequeue returns nil.
- Remove force unwraps from participant row configuration.
- Keep cell construction free of recursive table reloads.
- Extend the static baseline so the fallback cell guard remains visible without Xcode.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
