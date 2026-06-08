#!/usr/bin/env python3
from pathlib import Path
import plistlib
import re
import shutil
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/plans/2026-06-08-card-roulette-baseline.md"


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
    plan = PLAN.read_text(encoding="utf-8") if PLAN.exists() else ""

    require(app_plist.get("CFBundlePackageType") == "APPL",
            "CardRoulette Info.plist must remain an application plist",
            failures)
    require(test_plist.get("CFBundlePackageType") == "BNDL",
            "CardRouletteTests Info.plist must remain a test bundle plist",
            failures)
    require("ViewController.swift in Sources" in project and "INFOPLIST_FILE = CardRoulette/Info.plist" in project,
            "Xcode project must keep view controller and plist wiring",
            failures)
    require("func pickAWinner() -> String?" in view_controller and "players.count == 0" in view_controller,
            "Winner selection must return nil for empty participant lists",
            failures)
    require("if self.players.count > 0" in view_controller and "if let event = event where event.subtype == UIEventSubtype.MotionShake && self.players.count > 0" in view_controller,
            "winner actions must be blocked when there are no participants",
            failures)
    require("Add participants first" in view_controller,
            "Winner segue must provide a fallback for empty participant lists",
            failures)
    require("arc4random_uniform(UInt32(players.count))" in view_controller,
            "Winner selection must use bounded random participant selection",
            failures)
    require("let scanner = NSScanner(string: cString)" in hex_source and "scanner.atEnd" in hex_source,
            "Hex parser must reject partial invalid scans",
            failures)
    add_controller = read("CardRoulette/AddParticipantViewController.swift")
    require("participantItem = nil" in add_controller and "text?.stringByTrimmingCharactersInSet" in add_controller and "participantName.isEmpty" in add_controller,
            "participant entry must trim names and ignore blank input",
            failures)
    cell_body = re.search(r"cellForRowAtIndexPath[\s\S]+?return cell!", view_controller)
    require(cell_body is not None and "tableView.reloadData()" not in cell_body.group(0),
            "cell construction must not recursively reload the table",
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
    require("make check" in readme and "CardRoulette.xcodeproj" in readme and "does not process payments" in readme,
            "README must document static verification, project usage, and payment boundary",
            failures)
    require("local-only" in readme.lower() and "participant" in readme.lower(),
            "README must document local-only participant data expectations",
            failures)
    require("scripts/check-baseline.py" in vision and "local-only" in vision.lower(),
            "VISION must describe the current static privacy baseline",
            failures)
    require("credit card" in security.lower() and "make check" in security,
            "SECURITY must document payment-data boundary and static baseline",
            failures)
    require("empty participant" in changes.lower() and "blank" in changes.lower() and "make check" in changes,
            "CHANGES must record the empty-list, blank-input, and baseline updates",
            failures)
    require("status: completed" in plan,
            "plan must be marked completed",
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
