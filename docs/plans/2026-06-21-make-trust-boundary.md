# Make Trust Boundary Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use test-driven development to implement this plan task-by-task.

**Goal:** Keep the local Make verification contract truthful about GNU Make caller authority and align workflow documentation with the checked-in macOS job.

**Architecture:** Preserve the application, project, XCTest, workflow, and native runner unchanged. Add a repository-owned Python regression harness that executes the real Makefile against isolated marker fixtures, then run that harness from the existing static baseline so documentation and boundary behavior cannot drift silently.

**Tech Stack:** GNU Make, Python standard library, POSIX shell, Xcode project metadata.

---

## Scope

1. Prove canonical and absolute-Makefile external-directory aliases execute the repository baseline.
2. Reproduce caller-selected shell/PATH tools, startup and later Makefiles,
   target-specific root overrides, replacement recipes, and no-execution modes.
3. Document those caller-controlled mechanisms outside the checked-in Makefile
   trust boundary rather than claiming the repository Makefile can prohibit them.
4. Correct the stale Ubuntu workflow statement to the actual `macos-15`
   `make test` job.
5. Keep app sources, project metadata, XCTest, workflow, native runner, and
   dependency state byte-for-byte unchanged.

## Test-First Evidence

The new regression harness was run before documentation or baseline integration.
Its canonical and hostile executable probes passed, while documentation checks
failed because the boundary language was absent and README still claimed an
Ubuntu baseline job. The minimal documentation and baseline integration changes
then made the same harness pass.

## Enforceable Contract

The local aliases are valid when invoked through the unmodified checked-in
Makefile with trusted shell and PATH tools and without caller-supplied extra or
startup Makefiles, target-specific overrides, replacement recipes, or
no-execution flags. GNU Make callers control parsing and execution outside that
contract; the repository documents and tests that fact instead of presenting a
convenience Makefile as a security boundary.
