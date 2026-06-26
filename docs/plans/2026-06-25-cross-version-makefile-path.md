# Cross-Version Explicit Makefile Path Contract

Status: Completed

## Problem

The Make trust-boundary harness required every GNU Make release to evaluate
`$(...)` syntax embedded in an explicit `-f` path before loading the repository.
GNU Make 3.81 follows that hazardous behavior, but GNU Make 4.3 treats an
existing path containing the same bytes literally. The single-outcome assertion
made the otherwise green SDK-free baseline fail on Linux.

The hostile-path probe also retained the prior safe-path baseline marker, so it
could not independently prove whether repository recipes ran.

## Scope

- Clear all markers between the shell-metacharacter and Make-syntax probes.
- Accept a pre-load expansion only when the hostile marker appears, Make fails,
  and repository recipes do not run.
- Accept literal-path handling only when no hostile marker appears, Make
  succeeds, and the repository baseline runs.
- Keep the cross-version-safe guidance to invoke `/usr/bin/make` from inside a
  checkout containing literal `$(` without an explicit `-f` path.

## Verification

- Reproduce the original failure with GNU Make 4.3.
- Run `python3 scripts/test-make-trust-boundary.py`.
- Run `/usr/bin/make check` and the complete `/usr/bin/make verify` gate.
- Require hosted macOS/XCTest and CodeQL checks on the exact pull-request head.

## Boundary

This changes only verification semantics and documentation. It does not relax
repository Make authority, execute untrusted checkout paths in hosted evidence,
or change application source, participant data, winner selection, persistence,
networking, or payment behavior.
