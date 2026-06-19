# AGENTS.md

## Repository purpose

`garethpaul/ios-credit-card-roulette` is an Apple platform application or Swift sample. Credit Card Roulette

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets
- `CardRoulette.xcodeproj` - Xcode project
- `CardRoulette` - repository source or sample assets
- `CardRouletteTests` - repository source or sample assets
- `img` - repository source or sample assets

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `make check`
- Hosted/local XCTest gate: `make test`
- Simulator overrides: `IOS_DESTINATION` or `IOS_SIMULATOR_NAME`
- Local Apple development: `open CardRoulette.xcodeproj`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: Swift (7).
- Preserve legacy Xcode project settings and signing assumptions unless the change is explicitly about modernization.

## Testing guidance

- Test-related files detected: `CardRouletteTests/CardRouletteTests.swift`
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- No required secret or credential file was identified in the repository scan. If you add integrations later, keep secrets out of git.
- Keep signing files, local xcconfig files, and environment files out of git.
- Participant names and payment choices should remain local-only. Do not add storage, upload, analytics, or real payment processing without a separate privacy and security design.
- Route shake winner actions from UIKit's authoritative motion argument and
  retain the typed participant gate.
- Preserve visible first-responder ownership so physical shake input reaches
  the roulette controller only while that screen is active.
- This looks like an Apple platform project or sample. Xcode, Swift, CocoaPods, and deployment target versions may need to match the original project era.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
