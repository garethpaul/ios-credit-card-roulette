#!/usr/bin/env python3
from pathlib import Path
import plistlib
import re
import shutil
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PLAN = ROOT / "docs/plans/2026-06-08-card-roulette-baseline.md"
WINNER_INPUT_PLAN = ROOT / "docs/plans/2026-06-08-winner-input-guard.md"
CELL_FALLBACK_PLAN = ROOT / "docs/plans/2026-06-08-table-cell-fallback.md"
PARTICIPANT_NORMALIZER_PLAN = ROOT / "docs/plans/2026-06-08-participant-name-normalizer.md"
UNWIND_SOURCE_PLAN = ROOT / "docs/plans/2026-06-09-unwind-source-guard.md"
PARTICIPANT_ARRAY_PLAN = ROOT / "docs/plans/2026-06-09-participant-array-type-guard.md"
PARTICIPANT_REMOVAL_PLAN = ROOT / "docs/plans/2026-06-09-participant-removal-index-guard.md"


def require(condition, message, failures):
    if not condition:
        failures.append(message)


def read(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


def strip_swift_line_comments(text):
    return "\n".join(line.split("//", 1)[0] for line in text.splitlines())


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
    required_files = [
        ".gitignore",
        "CHANGES.md",
        "Makefile",
        "README.md",
        "SECURITY.md",
        "VISION.md",
        "CardRoulette.xcodeproj/project.pbxproj",
        "CardRoulette.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
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
        "docs/plans/2026-06-08-winner-input-guard.md",
        "docs/plans/2026-06-08-table-cell-fallback.md",
        "docs/plans/2026-06-08-participant-name-normalizer.md",
        "docs/plans/2026-06-09-unwind-source-guard.md",
        "docs/plans/2026-06-09-participant-array-type-guard.md",
        "docs/plans/2026-06-09-participant-removal-index-guard.md",
        "img/app.gif",
    ]

    for relative_path in required_files:
        require((ROOT / relative_path).is_file(), f"Required file missing: {relative_path}", failures)

    for xml_file in [
        "CardRoulette.xcodeproj/project.xcworkspace/contents.xcworkspacedata",
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
    baseline_plan = BASELINE_PLAN.read_text(encoding="utf-8") if BASELINE_PLAN.exists() else ""
    winner_input_plan = WINNER_INPUT_PLAN.read_text(encoding="utf-8") if WINNER_INPUT_PLAN.exists() else ""
    cell_fallback_plan = CELL_FALLBACK_PLAN.read_text(encoding="utf-8") if CELL_FALLBACK_PLAN.exists() else ""
    participant_normalizer_plan = PARTICIPANT_NORMALIZER_PLAN.read_text(encoding="utf-8") if PARTICIPANT_NORMALIZER_PLAN.exists() else ""
    unwind_source_plan = UNWIND_SOURCE_PLAN.read_text(encoding="utf-8") if UNWIND_SOURCE_PLAN.exists() else ""
    participant_array_plan = PARTICIPANT_ARRAY_PLAN.read_text(encoding="utf-8") if PARTICIPANT_ARRAY_PLAN.exists() else ""
    participant_removal_plan = PARTICIPANT_REMOVAL_PLAN.read_text(encoding="utf-8") if PARTICIPANT_REMOVAL_PLAN.exists() else ""

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
    require("func pickAWinner() -> String?" in view_controller and
            "let participantItems = self.participantItems()" in view_controller and
            "participantItems.count == 0" in view_controller,
            "Winner selection must return nil when no typed participants are available",
            failures)
    require("if self.players.count > 0" in view_controller and "if let event = event where event.subtype == UIEventSubtype.MotionShake && self.players.count > 0" in view_controller,
            "winner actions must be blocked when there are no participants",
            failures)
    require("func participantItemFromSegueSource(source: AnyObject?) -> ParticipantListItem?" in view_controller and
            "source as? AddParticipantViewController" in view_controller and
            "source as? WinnerViewController" in view_controller and
            "as! AddParticipantViewController" not in view_controller,
            "unwind handling must accept known participant sources without force-casting",
            failures)
    require("Add participants first" in view_controller,
            "Winner segue must provide a fallback for empty participant lists",
            failures)
    winner_controller = read("CardRoulette/WinnerViewController.swift")
    require('winnerName ?? "Add participants first"' in winner_controller,
            "Winner screen must show a fallback when opened without a winner name",
            failures)
    participant_model = read("CardRoulette/ParticipantListItem.swift")
    require("class func normalizedName(name: String?) -> String?" in participant_model and
            "stringByTrimmingCharactersInSet" in participant_model and
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
            "objectAtIndex(index) as? ParticipantListItem" in view_controller and
            "arc4random_uniform(UInt32(participantItems.count))" in view_controller and
            "self.players.objectAtIndex(Int(randomIndex)) as!" not in view_controller,
            "Winner selection must filter the legacy player array before bounded random participant selection",
            failures)
    require("func participantItemAtIndex(index: Int) -> ParticipantListItem?" in view_controller and
            "return self.players.objectAtIndex(index) as? ParticipantListItem" in view_controller,
            "Participant table rendering must use a guarded participant accessor",
            failures)
    require("func removeParticipantAtIndex(index: Int) -> Bool" in view_controller and
            "self.players.removeObjectAtIndex(index)" in view_controller and
            "if self.removeParticipantAtIndex(indexPath.row)" in view_controller,
            "Participant row deletion must use a guarded removal helper",
            failures)
    require("let scanner = NSScanner(string: cString)" in hex_source and "scanner.atEnd" in hex_source,
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
            "testParticipantItemAtIndexRejectsInvalidEntries" in tests and
            "testRemoveParticipantAtIndexRemovesValidEntry" in tests and
            "testRemoveParticipantAtIndexRejectsInvalidIndexes" in tests and
            "XCTAssert(true" not in tests and "testPerformanceExample" not in tests,
            "CardRouletteTests must replace template tests with participant-name normalization assertions",
            failures)
    cell_body = re.search(r"cellForRowAtIndexPath[\s\S]+?return cell", view_controller)
    require(cell_body is not None and "tableView.reloadData()" not in cell_body.group(0),
            "cell construction must not recursively reload the table",
            failures)
    require(cell_body is not None and "?? UITableViewCell(style: .Default" in cell_body.group(0) and "cell!" not in cell_body.group(0),
            "cell construction must provide a fallback cell instead of force-unwrapping the dequeue result",
            failures)
    require("return UIColor.grayColor()" in hex_source,
            "Hex parser must keep gray fallback behavior",
            failures)
    require(not re.search(r"\b(?:print|println|NSLog)\s*\(", active_sources),
            "Participant/payment state must not be logged",
            failures)
    for forbidden in ["URLSession", "NSURLConnection", "NSURL", "http://", "https://", "UserDefaults", "writeToFile", "creditCardNumber"]:
        require(forbidden not in active_sources,
                f"Roulette sample must not add network, persistence, or card-data handling: {forbidden}",
                failures)
    swift_files = sorted((ROOT / "CardRoulette").rglob("*.swift")) + sorted((ROOT / "CardRouletteTests").rglob("*.swift"))
    require(len(swift_files) >= 7,
            "expected Swift source/test inventory is missing",
            failures)
    require("*.local.xcconfig" in gitignore and ".env" in gitignore and "DerivedData" in gitignore,
            ".gitignore must exclude local config and Xcode build products",
            failures)
    require("make check" in readme and "CardRoulette.xcodeproj" in readme and "does not process payments" in readme and
            "winner" in readme.lower() and "fallback cell" in readme.lower() and "normalization" in readme.lower() and
            "unwind" in readme.lower() and "typed participant" in readme.lower() and "participant removal" in readme.lower(),
            "README must document static verification, project usage, winner guards, typed participant guards, cell fallback, and payment boundary",
            failures)
    require("local-only" in readme.lower() and "participant" in readme.lower(),
            "README must document local-only participant data expectations",
            failures)
    require("scripts/check-baseline.py" in vision and "local-only" in vision.lower() and
            "fallback cell" in vision.lower() and "normalization" in vision.lower() and
            "unwind" in vision.lower() and "typed participant" in vision.lower() and "participant removal" in vision.lower(),
            "VISION must describe the current static privacy baseline",
            failures)
    require("credit card" in security.lower() and "make check" in security and
            "normalization" in security.lower() and "unwind" in security.lower() and
            "typed participant" in security.lower() and "participant removal" in security.lower(),
            "SECURITY must document payment-data boundary and static baseline",
            failures)
    require("empty participant" in changes.lower() and "blank" in changes.lower() and
            "winner" in changes.lower() and "fallback cell" in changes.lower() and
            "normalization" in changes.lower() and "unwind" in changes.lower() and "participant removal" in changes.lower() and "make check" in changes,
            "CHANGES must record the empty-list, blank-input, winner, normalization, fallback-cell, and baseline updates",
            failures)
    require("typed participant" in changes.lower(),
            "CHANGES must record typed participant array guard updates",
            failures)
    require("status: completed" in baseline_plan and "status: completed" in winner_input_plan and
            "status: completed" in cell_fallback_plan and "status: completed" in participant_normalizer_plan,
            "plans must be marked completed",
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

    if shutil.which("xcodebuild"):
        print("xcodebuild is available; run a scheme-specific Xcode test on macOS before release.")
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
