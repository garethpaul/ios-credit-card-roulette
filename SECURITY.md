# Security Policy

## Supported Versions

The supported security scope for `ios-credit-card-roulette` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: Credit Card Roulette

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/ios-credit-card-roulette` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be an Apple platform application or Swift sample. The active security scope is the code and documentation on the default branch.
- Review found network clients, sockets, web APIs, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- No primary dependency manifest was detected in the repository root. If dependencies are added later, include a manifest and prefer reproducible installation instructions.
- This sample must not collect, store, or process credit card numbers. Treat any real payment processing, persistence, analytics, or participant-data sharing as security-sensitive scope expansion.
- `make check` runs a static baseline that guards plist/storyboard metadata, Xcode project wiring, source inventory, participant-name normalization, participant unwind handling, typed and nonempty participant filtering, participant removal index checks, winner destination handling, navigation logo title view ownership, empty-list winner selection, winner-screen input handling, hex parser fallback behavior, and logging/network/persistence regressions when Xcode is unavailable.
- The checked-in Makefile fixes `/bin/sh`, repository-owned Python and Xcode
  launchers, and the canonical checkout root; it rejects replacement recipes,
  target-specific root/tool substitutions, and non-executing or error-ignoring modes.
- Startup Makefiles can execute parse-time code before rejection, and later
  double-colon recipes remain caller authority. Hosted verification avoids both.
- Make syntax in an explicit `-f` path may be evaluated before the repository
  loads on older GNU Make releases; newer releases can treat the path literally.
  Hostile checkout names containing literal `$(` must use the cross-version-safe
  invocation from inside the checkout without an explicit Makefile path.
- A typed winner trigger with a nonempty-name guard should prevent invalid
  legacy array entries from navigating to winner presentation.
- Participant normalization should reject names made only from Unicode
  whitespace, control, or format scalars so invisible entries cannot become
  rows or winners. Invisible boundary scalars should also be removed from
  otherwise visible names without stripping internal emoji joiners.
- Shake navigation should use UIKit's authoritative motion argument while
  retaining the typed participant gate.
- Visible first-responder ownership is limited to the active roulette screen;
  it does not add participant persistence, analytics, networking, or payment
  processing.
- Single-flight winner presentation rejects duplicate button or shake
  navigation while a winner transition is already in progress.
- Winner action availability is derived from typed participants with nonempty
  normalized names after each production mutation without persisting or exposing
  participant data.
- Visible participant rows should map through typed entries with nonempty
  normalized names before rendering or removal so malformed legacy values remain
  inert.
- The pinned GitHub Actions macOS workflow uses read-only repository permissions
  without persisted checkout credentials and executes the unit-test suite in an
  unsigned simulator build without participant persistence or upload, payment
  processing, deployment, or signing material.
- Do not add payment processing, participant upload, deployment, or credentialed
  service steps without a separate privacy and security review.

## Mobile Privacy Notes

If this project requests device permissions such as location, camera, microphone, contacts, Bluetooth, health data, or local storage access, reports should describe the permission involved and whether sensitive data can be accessed, persisted, or transmitted unexpectedly. Please avoid testing against real third-party user data or accounts you do not control.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
