# Make Trust Boundary Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use test-driven development to implement this plan task-by-task.

**Goal:** Enforce the repository-owned portion of the Make verification contract, document GNU Make's unavoidable caller boundary, and align the workflow with the checked-in macOS job.

**Architecture:** Preserve the application, project, XCTest, and app behavior. Freeze the shell, checkout root, Python runner, and Xcode runner in the Makefile; reject unsafe modes and replaceable recipes; and execute a repository-owned regression harness from the static baseline.

**Tech Stack:** GNU Make, Python standard library, POSIX shell, Xcode project metadata.

---

## Scope

1. Prove canonical and absolute-Makefile external-directory aliases execute the repository baseline.
2. Reject caller-selected shell/PATH tools, target-specific root/tool overrides,
   replacement recipes, and non-executing or error-ignoring modes.
3. Prove and document that startup Makefiles can execute parse-time code before rejection and later double-colon recipes remain caller authority.
4. Correct the stale Ubuntu workflow statement to the actual `macos-15`
   `make test` job.
5. Keep app sources, project metadata, XCTest, and dependency state unchanged.

## Test-First Evidence

The new regression harness was run before documentation or baseline integration.
Its canonical and hostile executable probes passed, while documentation checks
failed because the boundary language was absent and README still claimed an
Ubuntu baseline job. The minimal documentation and baseline integration changes
then made the same harness pass.

## Enforceable Contract

The local aliases fix `/bin/sh`, repository-owned Python and Xcode launchers,
and the canonical checkout root. They reject replacement recipes,
target-specific root/tool substitutions, and non-executing or error-ignoring modes.
Startup Makefiles can execute parse-time code before rejection, and later
double-colon recipes remain caller authority because GNU Make appends them after
the checked-in recipe. The harness proves both limits instead of overstating the
Makefile as a complete security boundary.
Make syntax in an explicit `-f` path may be evaluated before the repository
loads on older GNU Make releases, while newer releases can treat the same
existing path literally. The hostile-path proof accepts only those two bounded
outcomes. Paths containing literal `$(` should still be invoked from inside the
checkout without an explicit Makefile path for cross-version safety.
