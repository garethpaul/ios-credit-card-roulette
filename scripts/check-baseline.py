#!/usr/bin/env python3
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PLAN = ROOT / "docs/plans/2026-06-08-card-roulette-baseline.md"
MAKE_GATES_PLAN = ROOT / "docs/plans/2026-06-09-make-gate-aliases.md"
WINNER_INPUT_PLAN = ROOT / "docs/plans/2026-06-08-winner-input-guard.md"
CELL_FALLBACK_PLAN = ROOT / "docs/plans/2026-06-08-table-cell-fallback.md"
PARTICIPANT_NORMALIZER_PLAN = ROOT / "docs/plans/2026-06-08-participant-name-normalizer.md"
UNWIND_SOURCE_PLAN = ROOT / "docs/plans/2026-06-09-unwind-source-guard.md"
PARTICIPANT_ARRAY_PLAN = ROOT / "docs/plans/2026-06-09-participant-array-type-guard.md"
PARTICIPANT_REMOVAL_PLAN = ROOT / "docs/plans/2026-06-09-participant-removal-index-guard.md"
NAV_LOGO_PLAN = ROOT / "docs/plans/2026-06-09-navigation-logo-title-view.md"
WINNER_DESTINATION_PLAN = ROOT / "docs/plans/2026-06-10-winner-destination-guard.md"
CI_PLAN = ROOT / "docs/plans/2026-06-10-ci-baseline.md"
HOSTED_VALIDATION_PLAN = ROOT / "docs/plans/2026-06-10-hosted-project-validation.md"
SWIFT_5_BUILD_PLAN = ROOT / "docs/plans/2026-06-10-swift-5-app-build.md"
HOSTED_XCTEST_PLAN = ROOT / "docs/plans/2026-06-12-hosted-xctest.md"
PARTICIPANT_REMOVAL_TYPE_PLAN = ROOT / "docs/plans/2026-06-12-participant-removal-type-guard.md"
TYPED_WINNER_TRIGGER_PLAN = ROOT / "docs/plans/2026-06-13-typed-winner-trigger.md"
VISIBLE_PARTICIPANT_ROWS_PLAN = ROOT / "docs/plans/2026-06-13-visible-participant-rows.md"
EXPECTED_WORKFLOW = """name: Check

on:
  pull_request:
  push:
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: check-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  baseline:
    runs-on: macos-15
    timeout-minutes: 10
    steps:
      - name: Check out repository
        uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10 # v6.0.3
        with:
          persist-credentials: false
      - name: Validate roulette baseline and XCTest
        run: make test
"""
EXPECTED_MAKEFILE = """.PHONY: build check lint test

lint: check

test: check
\t@if command -v xcodebuild >/dev/null 2>&1; then ./scripts/run-tests.sh; else printf '%s\\n' "Skipping XCTest: xcodebuild is not installed."; fi

build: check

check:
\tpython3 scripts/check-baseline.py
"""


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def markdown_section(text, heading):
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


def strip_swift_line_comments(text):
    stripped_lines = []
    for line in text.splitlines():
        output = []
        in_string = False
        escaped = False
        index = 0
        while index < len(line):
            character = line[index]
            if not in_string and character == "/" and index + 1 < len(line) and line[index + 1] == "/":
                break
            output.append(character)
            if character == '"' and not escaped:
                in_string = not in_string
            if character == "\\":
                escaped = not escaped
            else:
                escaped = False
            index += 1
        stripped_lines.append("".join(output))
    return "\n".join(stripped_lines)


def swift_function_body(text, signature):
    start = text.find(signature)
    if start == -1:
        return ""

    body_start = text.find("{", start)
    if body_start == -1:
        return ""

    depth = 0
    for index in range(body_start, len(text)):
        character = text[index]
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return text[body_start + 1:index]
    return ""


def parse_xml(relative_path, failures):
    try:
        ET.parse(str(ROOT / relative_path))
    except ET.ParseError as error:
        failures.append(f"{relative_path} is not well-formed XML: {error}")


def parse_plist(relative_path, failures):
    try:
        with (ROOT / relative_path).open("rb") as file:
            return plistlib.load(file)
    except Exception as error:
        failures.append(f"{relative_path} is not a readable plist: {error}")
        return {}


def main():
    failures = []
    swift_comment_fixture = 'let endpoint = "http://example.com/path" // trailing comment'
    require(strip_swift_line_comments(swift_comment_fixture) ==
            'let endpoint = "http://example.com/path" ',
            "Swift comment stripping must preserve quoted URL strings",
            failures)
    required_files = [
        ".github/workflows/check.yml",
        ".gitignore",
        ".github/workflows/check.yml",
        "CHANGES.md",
        "Makefile",
        "README.md",
        "SECURITY.md",
        "VISION.md",
        "CardRoulette.xcodeproj/project.pbxproj",
        "CardRoulette.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
        "CardRoulette.xcodeproj/xcshareddata/xcschemes/CardRoulette.xcscheme",
        "CardRoulette/Info.plist",
        "CardRoulette/AppDelegate.swift",
        "CardRoulette/ViewController.swift",
        "CardRoulette/AddParticipantViewController.swift",
        "CardRoulette/WinnerViewController.swift",
        "CardRoulette/ParticipantListItem.swift",
        "CardRoulette/Hex.swift",
        "CardRouletteTests/CardRouletteTests.swift",
        "CardRouletteTests/Info.plist",
        "docs/readme-overview.svg",
        "docs/plans/2026-06-08-card-roulette-baseline.md",
        "docs/plans/2026-06-09-make-gate-aliases.md",
        "docs/plans/2026-06-08-winner-input-guard.md",
        "docs/plans/2026-06-08-table-cell-fallback.md",
        "docs/plans/2026-06-08-participant-name-normalizer.md",
        "docs/plans/2026-06-09-unwind-source-guard.md",
        "docs/plans/2026-06-09-participant-array-type-guard.md",
        "docs/plans/2026-06-09-participant-removal-index-guard.md",
        "docs/plans/2026-06-09-navigation-logo-title-view.md",
        "docs/plans/2026-06-10-winner-destination-guard.md",
        "docs/plans/2026-06-10-ci-baseline.md",
        "docs/plans/2026-06-10-hosted-project-validation.md",
        "docs/plans/2026-06-10-swift-5-app-build.md",
        "docs/plans/2026-06-12-hosted-xctest.md",
        "docs/plans/2026-06-12-participant-removal-type-guard.md",
        "docs/plans/2026-06-13-typed-winner-trigger.md",
        "docs/plans/2026-06-13-visible-participant-rows.md",
        "img/app.gif",
        "scripts/run-tests.sh",
    ]

    for relative_path in required_files:
        require((ROOT / relative_path).is_file(), f"Required file missing: {relative_path}", failures)

    for xml_file in [
        "CardRoulette.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
        "CardRoulette.xcodeproj/xcshareddata/xcschemes/CardRoulette.xcscheme",
        "CardRoulette/Base.lproj/Main.storyboard",
        "CardRoulette/Base.lproj/LaunchScreen.xib",
        "docs/readme-overview.svg",
    ]:
        parse_xml(xml_file, failures)

    app_plist = parse_plist("CardRoulette/Info.plist", failures)
    test_plist = parse_plist("CardRouletteTests/Info.plist", failures)
    project = read("CardRoulette.xcodeproj/project.pbxproj")
    view_controller = read("CardRoulette/ViewController.swift")
    tests = read("CardRouletteTests/CardRouletteTests.swift")
    active_sources = "\n".join(strip_swift_line_comments(read(path)) for path in [
        "CardRoulette/AppDelegate.swift",
        "CardRoulette/ViewController.swift",
        "CardRoulette/AddParticipantViewController.swift",
        "CardRoulette/WinnerViewController.swift",
        "CardRoulette/ParticipantListItem.swift",
        "CardRoulette/Hex.swift",
    ])
    hex_source = read("CardRoulette/Hex.swift")
    readme = read("README.md")
    vision = read("VISION.md")
    security = read("SECURITY.md")
    changes = read("CHANGES.md")
    gitignore = read(".gitignore")
    makefile = read("Makefile")
    test_runner = read("scripts/run-tests.sh")
    shared_scheme = read("CardRoulette.xcodeproj/xcshareddata/xcschemes/CardRoulette.xcscheme")
    baseline_plan = BASELINE_PLAN.read_text(encoding="utf-8") if BASELINE_PLAN.exists() else ""
    make_gates_plan = MAKE_GATES_PLAN.read_text(encoding="utf-8") if MAKE_GATES_PLAN.exists() else ""
    winner_input_plan = WINNER_INPUT_PLAN.read_text(encoding="utf-8") if WINNER_INPUT_PLAN.exists() else ""
    cell_fallback_plan = CELL_FALLBACK_PLAN.read_text(encoding="utf-8") if CELL_FALLBACK_PLAN.exists() else ""
    participant_normalizer_plan = PARTICIPANT_NORMALIZER_PLAN.read_text(encoding="utf-8") if PARTICIPANT_NORMALIZER_PLAN.exists() else ""
    unwind_source_plan = UNWIND_SOURCE_PLAN.read_text(encoding="utf-8") if UNWIND_SOURCE_PLAN.exists() else ""
    participant_array_plan = PARTICIPANT_ARRAY_PLAN.read_text(encoding="utf-8") if PARTICIPANT_ARRAY_PLAN.exists() else ""
    participant_removal_plan = PARTICIPANT_REMOVAL_PLAN.read_text(encoding="utf-8") if PARTICIPANT_REMOVAL_PLAN.exists() else ""
    nav_logo_plan = NAV_LOGO_PLAN.read_text(encoding="utf-8") if NAV_LOGO_PLAN.exists() else ""
    winner_destination_plan = WINNER_DESTINATION_PLAN.read_text(encoding="utf-8") if WINNER_DESTINATION_PLAN.exists() else ""
    ci_plan = CI_PLAN.read_text(encoding="utf-8") if CI_PLAN.exists() else ""
    hosted_validation_plan = HOSTED_VALIDATION_PLAN.read_text(encoding="utf-8") if HOSTED_VALIDATION_PLAN.exists() else ""
    swift_5_build_plan = SWIFT_5_BUILD_PLAN.read_text(encoding="utf-8") if SWIFT_5_BUILD_PLAN.exists() else ""
    hosted_xctest_plan = HOSTED_XCTEST_PLAN.read_text(encoding="utf-8") if HOSTED_XCTEST_PLAN.exists() else ""
    participant_removal_type_plan = PARTICIPANT_REMOVAL_TYPE_PLAN.read_text(encoding="utf-8") if PARTICIPANT_REMOVAL_TYPE_PLAN.exists() else ""
    typed_winner_trigger_plan = TYPED_WINNER_TRIGGER_PLAN.read_text(encoding="utf-8") if TYPED_WINNER_TRIGGER_PLAN.exists() else ""
    visible_participant_rows_plan = VISIBLE_PARTICIPANT_ROWS_PLAN.read_text(encoding="utf-8") if VISIBLE_PARTICIPANT_ROWS_PLAN.exists() else ""
    workflow = read(".github/workflows/check.yml")

    subprocess.check_call(["sh", "-n", "scripts/run-tests.sh"], cwd=ROOT)
    require((ROOT / "scripts/run-tests.sh").stat().st_mode & 0o111,
            "scripts/run-tests.sh must be executable",
            failures)

    require(app_plist.get("CFBundlePackageType") == "APPL",
            "CardRoulette Info.plist must remain an application plist",
            failures)
    require(test_plist.get("CFBundlePackageType") == "BNDL",
            "CardRouletteTests Info.plist must remain a test bundle plist",
            failures)
    require("ViewController.swift in Sources" in project and "INFOPLIST_FILE = CardRoulette/Info.plist" in project,
            "Xcode project must keep view controller and plist wiring",
            failures)
    require("ENABLE_TESTABILITY = YES;" in project and "@testable import CardRoulette" in tests,
            "Xcode project and tests must keep CardRoulette app code testable from XCTest",
            failures)
    require(project.count("IPHONEOS_DEPLOYMENT_TARGET = 12.0;") == 2 and
            "IPHONEOS_DEPLOYMENT_TARGET = 8.3;" not in project and
            project.count("SWIFT_VERSION = 5.0;") == 4,
            "Xcode project must use Swift 5 with the iOS 12 deployment target",
            failures)
    require("[UIApplication.LaunchOptionsKey: Any]?" in active_sources and
            "func application(_ application: UIApplication" in active_sources,
            "AppDelegate must use the Swift 5 launch-options signature",
            failures)
    controller_sources = {
        "ViewController": view_controller,
        "AddParticipantViewController": read("CardRoulette/AddParticipantViewController.swift"),
        "WinnerViewController": read("CardRoulette/WinnerViewController.swift"),
    }
    for controller_name, controller_source in controller_sources.items():
        require("self.navigationItem.titleView = logoView" in controller_source and
                "navigationController?.view.addSubview(logoView)" not in controller_source and
                "bringSubviewToFront(logoView)" not in controller_source and
                "logoView.frame.origin" not in controller_source,
                f"{controller_name} must scope the card logo to the navigation item title view",
                failures)
    require("func pickAWinner() -> String?" in view_controller and
            "let participantItems = self.participantItems()" in view_controller and
            "participantItems.isEmpty" in view_controller,
            "Winner selection must return nil when no typed participants are available",
            failures)
    require("func canPickWinner() -> Bool" in view_controller and
            "return !self.participantItems().isEmpty" in view_controller and
            "if self.canPickWinner()" in view_controller and
            "event?.subtype == .motionShake && self.canPickWinner()" in view_controller and
            "self.players.count > 0" not in view_controller,
            "button and shake winner actions must require a typed participant",
            failures)
    require("func participantItemFromSegueSource(_ source: Any?) -> ParticipantListItem?" in view_controller and
            "source as? AddParticipantViewController" in view_controller and
            "source as? WinnerViewController" in view_controller and
            "as! AddParticipantViewController" not in view_controller,
            "unwind handling must accept known participant sources without force-casting",
            failures)
    require("Add participants first" in view_controller,
            "Winner segue must provide a fallback for empty participant lists",
            failures)
    require("func configureWinnerDestination(_ destination: Any) -> Bool" in view_controller and
            "destination as? WinnerViewController" in view_controller and
            "configureWinnerDestination(segue.destination)" in view_controller and
            "segue.destinationViewController as! WinnerViewController" not in view_controller,
            "Winner segue destination must be type-checked before configuration",
            failures)
    winner_controller = read("CardRoulette/WinnerViewController.swift")
    require('winnerName ?? "Add participants first"' in winner_controller,
            "Winner screen must show a fallback when opened without a winner name",
            failures)
    participant_model = read("CardRoulette/ParticipantListItem.swift")
    require("class func normalizedName(_ name: String?) -> String?" in participant_model and
            "trimmingCharacters(in: .whitespacesAndNewlines)" in participant_model and
            "participantName.isEmpty" in participant_model and "return nil" in participant_model,
            "ParticipantListItem must expose a shared optional name normalizer",
            failures)
    require("participantItem = nil" in winner_controller and "ParticipantListItem.normalizedName" in winner_controller,
            "Winner participant entry must use the shared normalizer and ignore blank input",
            failures)
    require("textfield.text!" not in winner_controller,
            "Winner participant entry must not force-unwrap text field contents",
            failures)
    require("func participantItems() -> [ParticipantListItem]" in view_controller and
            "object(at: index) as? ParticipantListItem" in view_controller and
            "Int.random(in: participantItems.indices)" in view_controller and
            "arc4random_uniform" not in view_controller and
            "self.players.objectAtIndex(Int(randomIndex)) as!" not in view_controller,
            "Winner selection must filter the legacy player array before bounded random participant selection",
            failures)
    require("func participantItemAtIndex(_ index: Int) -> ParticipantListItem?" in view_controller and
            "return self.players.object(at: index) as? ParticipantListItem" in view_controller,
            "Participant table rendering must use a guarded participant accessor",
            failures)
    require("func removeParticipantAtIndex(_ index: Int) -> Bool" in view_controller and
            "object(at: index) is ParticipantListItem" in view_controller and
            "self.players.removeObject(at: index)" in view_controller,
            "Raw participant deletion must preserve its typed index guard",
            failures)
    visible_index_body = swift_function_body(view_controller, "func playerIndexForParticipantRow")
    visible_item_body = swift_function_body(view_controller, "func participantItemForVisibleRow")
    visible_removal_body = swift_function_body(view_controller, "func removeParticipantForVisibleRow")
    row_count_body = swift_function_body(view_controller, "numberOfRowsInSection")
    row_selection_body = swift_function_body(view_controller, "didSelectRowAt")
    require("participantRow < 0" in visible_index_body and
            "object(at: playerIndex) is ParticipantListItem" in visible_index_body and
            "visibleRow == participantRow" in visible_index_body and
            "visibleRow += 1" in visible_index_body,
            "Visible participant rows must map through typed entries",
            failures)
    require("playerIndexForParticipantRow(participantRow)" in visible_item_body and
            "participantItemAtIndex(playerIndex)" in visible_item_body and
            "playerIndexForParticipantRow(participantRow)" in visible_removal_body and
            "removeParticipantAtIndex(playerIndex)" in visible_removal_body,
            "Visible participant reads and removals must share the typed row mapping",
            failures)
    require("return self.participantItems().count" in row_count_body and
            "self.players.count" not in row_count_body and
            "participantItemForVisibleRow(indexPath.row)" in view_controller and
            "removeParticipantForVisibleRow(indexPath.row)" in row_selection_body and
            "removeParticipantAtIndex(indexPath.row)" not in row_selection_body,
            "Table rendering and selection must use visible typed participant rows",
            failures)
    require("let scanner = Scanner(string: cString)" in hex_source and "scanner.isAtEnd" in hex_source,
            "Hex parser must reject partial invalid scans",
            failures)
    add_controller = read("CardRoulette/AddParticipantViewController.swift")
    require("participantItem = nil" in add_controller and "ParticipantListItem.normalizedName" in add_controller,
            "participant entry must use the shared normalizer and ignore blank input",
            failures)
    require("testParticipantNameNormalizationTrimsWhitespace" in tests and "XCTAssertEqual" in tests and
            "testParticipantNameNormalizationRejectsBlankNames" in tests and "XCTAssertNil" in tests and
            "testParticipantItemFromAddParticipantSource" in tests and
            "testParticipantItemFromWinnerSource" in tests and
            "testParticipantItemFromUnknownSourceReturnsNil" in tests and
            "testParticipantItemsIgnoreInvalidPlayerEntries" in tests and
            "testCanPickWinnerRejectsEmptyAndInvalidOnlyPlayers" in tests and
            "testCanPickWinnerAcceptsTypedParticipantAmongInvalidEntries" in tests and
            tests.count("XCTAssertFalse(controller.canPickWinner()") == 2 and
            "XCTAssertTrue(controller.canPickWinner()" in tests and
            "testParticipantItemAtIndexRejectsInvalidEntries" in tests and
            "testRemoveParticipantAtIndexRemovesValidEntry" in tests and
            "testRemoveParticipantAtIndexRejectsInvalidIndexes" in tests and
            "testRemoveParticipantAtIndexRejectsInvalidEntryType" in tests and
            "testVisibleParticipantRowsIgnoreInvalidEntries" in tests and
            "testVisibleParticipantRemovalMapsToTypedEntry" in tests and
            "testVisibleParticipantRowsRejectInvalidIndexes" in tests and
            "Unrelated invalid entries should remain untouched" in tests and
            "testConfigureWinnerDestinationRejectsUnexpectedDestination" in tests and
            "testConfigureWinnerDestinationSetsFallbackWithoutParticipants" in tests and
            "testConfigureWinnerDestinationSetsTypedParticipantWinner" in tests and
            "XCTAssert(true" not in tests and "testPerformanceExample" not in tests,
            "CardRouletteTests must replace template tests with participant-name normalization assertions",
            failures)
    cell_body = re.search(r"cellForRowAt[\s\S]+?return cell", view_controller)
    require(cell_body is not None and "tableView.reloadData()" not in cell_body.group(0),
            "cell construction must not recursively reload the table",
            failures)
    require(cell_body is not None and "?? UITableViewCell(style: .default" in cell_body.group(0) and "cell!" not in cell_body.group(0),
            "cell construction must provide a fallback cell instead of force-unwrapping the dequeue result",
            failures)
    require("return .gray" in hex_source,
            "Hex parser must keep gray fallback behavior",
            failures)
    require(not re.search(r"\b(?:print|println|NSLog)\s*\(", active_sources),
            "Participant/payment state must not be logged",
            failures)
    for forbidden in ["URLSession", "NSURLConnection", "NSURL", "http://", "https://", "UserDefaults", "writeToFile"]:
        require(forbidden not in active_sources,
                f"Roulette sample must not add network, persistence, or card-data handling: {forbidden}",
                failures)
    active_sources_lower = active_sources.lower()
    for forbidden in ["creditcardnumber", "paymentprocessor", "storekit", "passkit", "pkpayment", "stripe", "braintree"]:
        require(forbidden not in active_sources_lower,
                f"Roulette sample must not add payment processing: {forbidden}",
                failures)
    swift_files = sorted((ROOT / "CardRoulette").rglob("*.swift")) + sorted((ROOT / "CardRouletteTests").rglob("*.swift"))
    require(len(swift_files) >= 7,
            "expected Swift source/test inventory is missing",
            failures)
    require("*.local.xcconfig" in gitignore and ".env" in gitignore and "DerivedData" in gitignore,
            ".gitignore must exclude local config and Xcode build products",
            failures)
    require(makefile == EXPECTED_MAKEFILE,
            "Makefile must exactly preserve static and XCTest verification gates",
            failures)
    require("xcrun simctl list devices available" in test_runner and
            "IOS_DESTINATION" in test_runner and "IOS_SIMULATOR_NAME" in test_runner and
            '-scheme "$SCHEME"' in test_runner and '-destination "$DESTINATION"' in test_runner and
            "CODE_SIGNING_ALLOWED=NO" in test_runner and "test" in test_runner,
            "test runner must discover or accept a simulator and execute unsigned XCTest",
            failures)
    require("iPhone 5" not in test_runner,
            "test runner must not use a retired fixed simulator",
            failures)
    require(shared_scheme.count('BlueprintIdentifier = "FDAE1E6E1B1A487600A89C51"') >= 2 and
            shared_scheme.count('BlueprintIdentifier = "FDAE1E831B1A487600A89C51"') >= 2 and
            '<TestableReference' in shared_scheme and 'skipped = "NO"' in shared_scheme,
            "shared scheme must build the app and execute CardRouletteTests",
            failures)
    require("make lint" in readme and "make test" in readme and "make build" in readme and "make check" in readme and "GitHub Actions" in readme and "CardRoulette.xcodeproj" in readme and "does not process payments" in readme and
            "winner" in readme.lower() and "fallback cell" in readme.lower() and "normalization" in readme.lower() and
            "unwind" in readme.lower() and "typed participant" in readme.lower() and "participant removal" in readme.lower() and
            "winner destination" in readme.lower() and "title view" in readme.lower(),
            "README must document static verification, project usage, winner guards, typed participant guards, cell fallback, and payment boundary",
            failures)
    require("typed winner trigger" in readme.lower(),
            "README must document typed winner trigger eligibility",
            failures)
    require("visible participant row" in readme.lower(),
            "README must document typed visible-row filtering",
            failures)
    require("local-only" in readme.lower() and "participant" in readme.lower(),
            "README must document local-only participant data expectations",
            failures)
    require("scripts/check-baseline.py" in vision and "make lint" in vision and "make test" in vision and "make build" in vision and "GitHub Actions" in vision and "local-only" in vision.lower() and
            "fallback cell" in vision.lower() and "normalization" in vision.lower() and
            "unwind" in vision.lower() and "typed participant" in vision.lower() and "participant removal" in vision.lower() and
            "winner destination" in vision.lower() and "title view" in vision.lower(),
            "VISION must describe the current static privacy baseline",
            failures)
    require("typed winner trigger" in vision.lower(),
            "VISION must preserve typed winner trigger eligibility",
            failures)
    require("visible participant row" in vision.lower(),
            "VISION must preserve typed visible-row filtering",
            failures)
    require("credit card" in security.lower() and "make check" in security and "GitHub Actions" in security and
            "normalization" in security.lower() and "unwind" in security.lower() and
            "typed participant" in security.lower() and "participant removal" in security.lower() and
            "winner destination" in security.lower() and "title view" in security.lower(),
            "SECURITY must document payment-data boundary and static baseline",
            failures)
    require("typed winner trigger" in security.lower(),
            "SECURITY must document typed winner trigger hardening",
            failures)
    require("visible participant row" in security.lower(),
            "SECURITY must document typed visible-row filtering",
            failures)
    require("GitHub Actions" in changes and "empty participant" in changes.lower() and "blank" in changes.lower() and
            "winner" in changes.lower() and "fallback cell" in changes.lower() and "title view" in changes.lower() and
            "normalization" in changes.lower() and "unwind" in changes.lower() and "participant removal" in changes.lower() and
            "winner destination" in changes.lower() and "make check" in changes and "make lint" in changes and "make test" in changes and "make build" in changes,
            "CHANGES must record the empty-list, blank-input, winner, normalization, fallback-cell, and baseline updates",
            failures)
    require("typed participant" in changes.lower(),
            "CHANGES must record typed participant array guard updates",
            failures)
    require("typed winner trigger" in changes.lower(),
            "CHANGES must record typed winner trigger eligibility",
            failures)
    require("visible participant row" in changes.lower(),
            "CHANGES must record typed visible-row filtering",
            failures)
    require("status: completed" in baseline_plan and "status: completed" in winner_input_plan and
            "status: completed" in cell_fallback_plan and "status: completed" in participant_normalizer_plan,
            "plans must be marked completed",
            failures)
    require("status: completed" in make_gates_plan,
            "make gate aliases plan must be marked completed",
            failures)
    require("status: completed" in unwind_source_plan,
            "unwind source guard plan must be marked completed",
            failures)
    require("status: completed" in participant_array_plan,
            "participant array type guard plan must be marked completed",
            failures)
    require("status: completed" in participant_removal_plan,
            "participant removal index guard plan must be marked completed",
            failures)
    require("status: completed" in nav_logo_plan,
            "navigation logo title-view plan must be marked completed",
            failures)
    require("status: completed" in winner_destination_plan,
            "winner destination guard plan must be marked completed",
            failures)
    require("status: completed" in ci_plan and "GitHub Actions" in ci_plan and "make check" in ci_plan,
            "CI baseline plan must record hosted make check verification",
            failures)
    require("status: completed" in hosted_validation_plan and "make check" in hosted_validation_plan,
            "hosted project validation plan must be completed and document make check",
            failures)
    require("status: completed" in swift_5_build_plan and "simulator" in swift_5_build_plan.lower(),
            "Swift 5 app build plan must be completed and document simulator verification",
            failures)
    require("status: completed" in hosted_xctest_plan and "make test" in hosted_xctest_plan and
            "hosted macOS XCTest run" in hosted_xctest_plan,
            "hosted XCTest plan must record the completed executable test contract",
            failures)
    require("status: completed" in typed_winner_trigger_plan and
            "All four Make gates" in typed_winner_trigger_plan and
            "hostile mutations" in typed_winner_trigger_plan.lower(),
            "typed winner trigger plan must record completed status and actual verification",
            failures)
    visible_rows_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", visible_participant_rows_plan
    )
    visible_rows_work = markdown_section(
        visible_participant_rows_plan, "Work Completed"
    )
    visible_rows_verification = markdown_section(
        visible_participant_rows_plan, "Verification Completed"
    )
    require(visible_rows_status == ["completed"] and visible_rows_work,
            "visible participant rows plan must record one completed status and completed work",
            failures)
    require(visible_rows_verification and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", visible_rows_verification) and
            "All four Make gates" in visible_rows_verification and
            "seven hostile mutations" in visible_rows_verification.lower() and
            "xcodebuild was unavailable" in visible_rows_verification,
            "visible participant rows plan must record completed local verification",
            failures)
    participant_removal_type_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", participant_removal_type_plan
    )
    participant_removal_type_work = markdown_section(
        participant_removal_type_plan, "Work Completed"
    )
    participant_removal_type_verification = markdown_section(
        participant_removal_type_plan, "Verification Completed"
    )
    require(participant_removal_type_status == ["completed"] and
            participant_removal_type_work,
            "participant removal type-guard plan must record one completed status and completed work",
            failures)
    require(participant_removal_type_verification and
            not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", participant_removal_type_verification),
            "participant removal type-guard plan must record finished verification without pending markers",
            failures)
    for evidence in [
        "make check",
        "make lint",
        "make test",
        "make build",
        "python3 -m py_compile scripts/check-baseline.py",
        "sh -n scripts/run-tests.sh",
        "git diff --check",
        "27394766979",
        "27394770140",
        "27394960091",
        "27402323075",
        "73dd879cbcd09553aa11d6f4cc4257b02fc62cea",
        "041c56d77acfd534eab38eda6c9308b01e7582b6",
        "object(at: index) is ParticipantListItem",
        "testRemoveParticipantAtIndexRejectsInvalidEntryType",
    ]:
        require(evidence in participant_removal_type_verification,
                f"participant removal type-guard plan must preserve verification evidence: {evidence}",
                failures)
    require(workflow == EXPECTED_WORKFLOW,
            "Check workflow must exactly match the bounded, credential-free macOS XCTest contract",
            failures)

    if shutil.which("xcodebuild"):
        result = subprocess.run(
            [
                "xcodebuild",
                "-list",
                "-project", "CardRoulette.xcodeproj",
            ],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        require(result.returncode == 0,
                "xcodebuild could not parse the CardRoulette project: " + result.stdout.strip(),
                failures)
    else:
        print("xcodebuild unavailable; static iOS baseline only.")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("ios-credit-card-roulette baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
