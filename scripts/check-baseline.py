#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import os
import plistlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
XCODEBUILD_PATH = Path("/usr/bin/xcodebuild")
OPENSTEP_SPEC = importlib.util.spec_from_file_location(
    "openstep_pbx", ROOT / "scripts/openstep_pbx.py"
)
OPENSTEP_PBX = importlib.util.module_from_spec(OPENSTEP_SPEC)
OPENSTEP_SPEC.loader.exec_module(OPENSTEP_PBX)
OpenStepParseError = OPENSTEP_PBX.OpenStepParseError
parse_openstep = OPENSTEP_PBX.parse_openstep
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
LOCATION_INDEPENDENT_MAKE_PLAN = ROOT / "docs/plans/2026-06-13-location-independent-make.md"
SHAKE_MOTION_PLAN = ROOT / "docs/plans/2026-06-14-shake-motion-routing.md"
SHAKE_RESPONDER_PLAN = ROOT / "docs/plans/2026-06-16-shake-first-responder-lifecycle.md"
WINNER_SINGLE_FLIGHT_PLAN = ROOT / "docs/plans/2026-06-16-winner-presentation-single-flight.md"
WINNER_ACTION_AVAILABILITY_PLAN = ROOT / "docs/plans/2026-06-18-winner-action-availability.md"
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
        run: /usr/bin/make test
"""

TARGET_CONFIGURATION_TOPOLOGY = (
    (
        "CardRoulette",
        "FDAE1E6E1B1A487600A89C51",
        "FDAE1E8E1B1A487600A89C51",
        "FDAE1E6F1B1A487600A89C51",
        "wrapper.application",
        "CardRoulette.app",
        "com.apple.product-type.application",
        "CardRoulette/Info.plist",
        "com.gpj.CardRoulette",
        (
            ("Debug", "FDAE1E8F1B1A487600A89C51"),
            ("Release", "FDAE1E901B1A487600A89C51"),
        ),
    ),
    (
        "CardRouletteTests",
        "FDAE1E831B1A487600A89C51",
        "FDAE1E911B1A487600A89C51",
        "FDAE1E841B1A487600A89C51",
        "wrapper.cfbundle",
        "CardRouletteTests.xctest",
        "com.apple.product-type.bundle.unit-test",
        "CardRouletteTests/Info.plist",
        "com.gpj.CardRouletteTests",
        (
            ("Debug", "FDAE1E921B1A487600A89C51"),
            ("Release", "FDAE1E931B1A487600A89C51"),
        ),
    ),
)


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


def pbx_dictionary(value):
    return value if isinstance(value, dict) else {}


def pbx_array(value):
    return value if isinstance(value, list) else []


def pbx_has_unquoted_key(dictionary, expected_key):
    return any(key == expected_key and not getattr(key, "quoted", False)
               for key in dictionary)


def pbx_is_unquoted(value):
    return isinstance(value, str) and not getattr(value, "quoted", False)


def pbx_canonical_unsigned_integer(value):
    if (not pbx_is_unquoted(value)
            or len(value) > 3
            or not re.fullmatch(r"0|[1-9][0-9]*", value)):
        return None
    return int(value)


def pbx_conditional_setting_keys(dictionary, setting_name):
    prefix = setting_name + "["
    return tuple(key for key in dictionary if str(key).startswith(prefix))


def validate_project_topology(project, app_plist, test_plist, failures):
    require(app_plist.get("CFBundlePackageType") == "APPL",
            "CardRoulette Info.plist must remain an application plist",
            failures)
    require(test_plist.get("CFBundlePackageType") == "BNDL",
            "CardRouletteTests Info.plist must remain a test bundle plist",
            failures)
    require(app_plist.get("CFBundleIdentifier") == "com.gpj.$(PRODUCT_NAME:rfc1034identifier)",
            "CardRoulette Info.plist must preserve the product-name bundle identifier template",
            failures)
    require(test_plist.get("CFBundleIdentifier") == "com.gpj.$(PRODUCT_NAME:rfc1034identifier)",
            "CardRouletteTests Info.plist must preserve the product-name bundle identifier template",
            failures)

    try:
        parsed_project = parse_openstep(project)
    except OpenStepParseError as error:
        failures.append("Xcode project must be valid OpenStep syntax: " + str(error))
        return

    root = pbx_dictionary(parsed_project)
    archive_version = pbx_canonical_unsigned_integer(root.get("archiveVersion"))
    object_version = pbx_canonical_unsigned_integer(root.get("objectVersion"))
    classes = root.get("classes")
    objects_value = root.get("objects")
    objects = pbx_dictionary(objects_value)
    require(pbx_has_unquoted_key(root, "archiveVersion") and archive_version == 1,
            "Xcode project archiveVersion must be the canonical supported value 1",
            failures)
    require(pbx_has_unquoted_key(root, "objectVersion")
            and object_version is not None
            and 42 <= object_version <= 90,
            "Xcode project objectVersion must be a canonical supported integer from 42 through 90",
            failures)
    require(pbx_has_unquoted_key(root, "classes") and isinstance(classes, dict),
            "Xcode project classes must be a dictionary",
            failures)
    require(pbx_has_unquoted_key(root, "objects")
            and isinstance(objects_value, dict)
            and bool(objects),
            "Xcode project must contain a nonempty objects dictionary",
            failures)
    require(pbx_has_unquoted_key(root, "rootObject")
            and pbx_is_unquoted(root.get("rootObject"))
            and root.get("rootObject") == "FDAE1E671B1A487600A89C51",
            "Xcode project must preserve the exact root project UUID",
            failures)

    project_object = pbx_dictionary(objects.get("FDAE1E671B1A487600A89C51"))
    expected_target_uuids = tuple(
        topology[1] for topology in TARGET_CONFIGURATION_TOPOLOGY
    )
    project_target_uuids = tuple(pbx_array(project_object.get("targets")))
    require(
        project_object.get("isa") == "PBXProject"
        and len(project_target_uuids) == len(expected_target_uuids)
        and all(
            pbx_is_unquoted(target_uuid)
            and re.fullmatch(r"[A-F0-9]{24}", target_uuid)
            for target_uuid in project_target_uuids
        )
        and frozenset(project_target_uuids) == frozenset(expected_target_uuids),
        "Xcode project must preserve exact unique app/test target UUID membership",
        failures,
    )
    native_target_uuids = tuple(
        object_uuid for object_uuid, value in objects.items()
        if pbx_dictionary(value).get("isa") == "PBXNativeTarget"
    )
    require(
        len(native_target_uuids) == len(TARGET_CONFIGURATION_TOPOLOGY)
        and frozenset(native_target_uuids) == frozenset(
            topology[1] for topology in TARGET_CONFIGURATION_TOPOLOGY
        ),
        "Xcode project must contain only the exact app/test PBXNativeTarget UUIDs",
        failures,
    )

    for (target_name, target_uuid, configuration_list_uuid, product_uuid,
         product_file_type, product_path, product_type, plist_path,
         bundle_identifier, configurations) in TARGET_CONFIGURATION_TOPOLOGY:
        target = pbx_dictionary(objects.get(target_uuid))
        require(bool(target),
                f"Xcode project must preserve the unique {target_name} target UUID {target_uuid}",
                failures)
        require(pbx_has_unquoted_key(target, "isa")
                and target.get("isa") == "PBXNativeTarget",
                f"{target_name} target UUID must remain a PBXNativeTarget",
                failures)
        require(pbx_has_unquoted_key(target, "name")
                and pbx_is_unquoted(target.get("name"))
                and target.get("name") == target_name,
                f"{target_name} target UUID must retain the exact target name",
                failures)
        require(pbx_has_unquoted_key(target, "productName")
                and pbx_is_unquoted(target.get("productName"))
                and target.get("productName") == target_name,
                f"{target_name} target must retain productName {target_name}",
                failures)
        require(target.get("buildConfigurationList") == configuration_list_uuid,
                f"{target_name} target must remain wired to configuration list {configuration_list_uuid}",
                failures)
        require(target.get("productReference") == product_uuid,
                f"{target_name} target must remain wired to product {product_uuid}",
                failures)
        require(target.get("productType") == product_type,
                f"{target_name} target must retain product type {product_type}",
                failures)

        product = pbx_dictionary(objects.get(product_uuid))
        require(bool(product),
                f"Xcode project must preserve the unique {target_name} product UUID {product_uuid}",
                failures)
        require(product.get("isa") == "PBXFileReference",
                f"{target_name} product UUID must remain a PBXFileReference",
                failures)
        require(product.get("explicitFileType") == product_file_type,
                f"{target_name} product must retain file type {product_file_type}",
                failures)
        require(product.get("path") == product_path,
                f"{target_name} product must retain path {product_path}",
                failures)
        require(product.get("sourceTree") == "BUILT_PRODUCTS_DIR",
                f"{target_name} product must remain in BUILT_PRODUCTS_DIR",
                failures)

        configuration_list = pbx_dictionary(objects.get(configuration_list_uuid))
        build_configuration_uuids = tuple(
            pbx_array(configuration_list.get("buildConfigurations"))
        )
        expected_configuration_uuids = frozenset(
            configuration_uuid for _, configuration_uuid in configurations
        )
        require(bool(configuration_list),
                f"Xcode project must preserve the unique {target_name} configuration list UUID {configuration_list_uuid}",
                failures)
        require(
            configuration_list.get("isa") == "XCConfigurationList"
            and len(build_configuration_uuids) == len(expected_configuration_uuids)
            and frozenset(build_configuration_uuids) == expected_configuration_uuids,
            f"{target_name} configuration list must preserve the exact unique Debug/Release UUID membership",
            failures,
        )

        for configuration_name, configuration_uuid in configurations:
            configuration = pbx_dictionary(objects.get(configuration_uuid))
            build_settings = pbx_dictionary(configuration.get("buildSettings"))
            require(bool(configuration),
                    f"Xcode project must preserve the unique {target_name} {configuration_name} configuration UUID {configuration_uuid}",
                    failures)
            require(configuration.get("isa") == "XCBuildConfiguration",
                    f"{target_name} {configuration_uuid} must remain an XCBuildConfiguration",
                    failures)
            require(configuration.get("name") == configuration_name,
                    f"{target_name} {configuration_uuid} must remain the {configuration_name} configuration",
                    failures)
            require(build_settings.get("INFOPLIST_FILE") == plist_path,
                    f"{target_name} {configuration_name} must use {plist_path}",
                    failures)
            require(pbx_has_unquoted_key(build_settings, "PRODUCT_BUNDLE_IDENTIFIER")
                    and pbx_is_unquoted(build_settings.get("PRODUCT_BUNDLE_IDENTIFIER"))
                    and build_settings.get("PRODUCT_BUNDLE_IDENTIFIER") == bundle_identifier,
                    f"{target_name} {configuration_name} must define exactly one "
                    f"PRODUCT_BUNDLE_IDENTIFIER = {bundle_identifier}",
                    failures)
            require(
                not pbx_conditional_setting_keys(
                    build_settings, "PRODUCT_BUNDLE_IDENTIFIER"
                ),
                f"{target_name} {configuration_name} must not define conditional "
                "PRODUCT_BUNDLE_IDENTIFIER variants",
                failures,
            )
            require(build_settings.get("PRODUCT_NAME") == "$(TARGET_NAME)",
                    f"{target_name} {configuration_name} must derive PRODUCT_NAME from the bound target name",
                    failures)
    bundle_identifier_owners = tuple(
        object_uuid for object_uuid, value in objects.items()
        if pbx_dictionary(value).get("isa") == "XCBuildConfiguration"
        and "PRODUCT_BUNDLE_IDENTIFIER" in pbx_dictionary(
            pbx_dictionary(value).get("buildSettings")
        )
    )
    expected_bundle_identifier_owners = frozenset(
        configuration_uuid
        for topology in TARGET_CONFIGURATION_TOPOLOGY
        for _, configuration_uuid in topology[-1]
    )
    require(
            len(bundle_identifier_owners) == len(expected_bundle_identifier_owners)
            and frozenset(bundle_identifier_owners) == expected_bundle_identifier_owners,
            "Xcode project must contain only the four active target-local bundle identifier mappings",
            failures)
    conditional_bundle_identifier_owners = tuple(
        object_uuid
        for object_uuid, value in objects.items()
        if pbx_dictionary(value).get("isa") == "XCBuildConfiguration"
        and pbx_conditional_setting_keys(
            pbx_dictionary(pbx_dictionary(value).get("buildSettings")),
            "PRODUCT_BUNDLE_IDENTIFIER",
        )
    )
    require(
        not conditional_bundle_identifier_owners,
        "Xcode project must not contain conditional PRODUCT_BUNDLE_IDENTIFIER mappings",
        failures,
    )


def parse_xcodebuild_settings(output, expected_keys=None):
    settings = {}
    for line in output.splitlines():
        match = re.match(r"^\s{4}([A-Z][A-Z0-9_]*) = (.*)$", line)
        if not match:
            continue
        key, value = match.groups()
        if expected_keys is not None and key not in expected_keys:
            continue
        if key in settings and settings[key] != value:
            raise ValueError(f"conflicting xcodebuild values for {key}")
        settings[key] = value
    return settings


def validate_effective_project_settings(xcodebuild, failures):
    for (target_name, _, _, _, _, _, product_type, plist_path,
         bundle_identifier, configurations) in TARGET_CONFIGURATION_TOPOLOGY:
        for configuration_name, _ in configurations:
            for sdk in ("iphoneos", "iphonesimulator"):
                expected = {
                    "TARGET_NAME": target_name,
                    "PRODUCT_NAME": target_name,
                    "PRODUCT_BUNDLE_IDENTIFIER": bundle_identifier,
                    "PRODUCT_TYPE": product_type,
                    "INFOPLIST_FILE": plist_path,
                }
                result = subprocess.run(
                    [
                        str(xcodebuild),
                        "-project", "CardRoulette.xcodeproj",
                        "-target", target_name,
                        "-configuration", configuration_name,
                        "-sdk", sdk,
                        "-showBuildSettings",
                    ],
                    cwd=ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                require(
                    result.returncode == 0,
                    f"xcodebuild could not resolve {target_name} {configuration_name} "
                    f"{sdk} settings: " + result.stdout.strip(),
                    failures,
                )
                if result.returncode != 0:
                    continue
                try:
                    settings = parse_xcodebuild_settings(result.stdout, expected)
                except ValueError as error:
                    failures.append(
                        f"xcodebuild returned ambiguous {target_name} {configuration_name} "
                        f"{sdk} settings: {error}"
                    )
                    continue
                for key, value in expected.items():
                    require(
                        settings.get(key) == value,
                        f"{target_name} {configuration_name} {sdk} effective {key} "
                        f"must be {value!r}, got {settings.get(key)!r}",
                        failures,
                    )


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
        "docs/plans/2026-06-13-location-independent-make.md",
        "docs/plans/2026-06-14-shake-motion-routing.md",
        "docs/plans/2026-06-16-shake-first-responder-lifecycle.md",
        "img/app.gif",
        "scripts/run-tests.sh",
        "scripts/run-python.sh",
        "scripts/run-xcodebuild.sh",
        "scripts/openstep_pbx.py",
        "scripts/test-make-trust-boundary.py",
        "scripts/test-project-topology.py",
        "docs/plans/2026-06-21-make-trust-boundary.md",
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
    location_independent_make_plan = LOCATION_INDEPENDENT_MAKE_PLAN.read_text(encoding="utf-8") if LOCATION_INDEPENDENT_MAKE_PLAN.exists() else ""
    shake_motion_plan = SHAKE_MOTION_PLAN.read_text(encoding="utf-8") if SHAKE_MOTION_PLAN.exists() else ""
    shake_responder_plan = SHAKE_RESPONDER_PLAN.read_text(encoding="utf-8") if SHAKE_RESPONDER_PLAN.exists() else ""
    winner_single_flight_plan = WINNER_SINGLE_FLIGHT_PLAN.read_text(encoding="utf-8") if WINNER_SINGLE_FLIGHT_PLAN.exists() else ""
    winner_action_availability_plan = WINNER_ACTION_AVAILABILITY_PLAN.read_text(encoding="utf-8") if WINNER_ACTION_AVAILABILITY_PLAN.exists() else ""
    workflow = read(".github/workflows/check.yml")

    subprocess.check_call(["/bin/sh", "-n", "scripts/run-tests.sh"], cwd=ROOT)
    subprocess.check_call([sys.executable, "scripts/test-make-trust-boundary.py"], cwd=ROOT)
    for executable in ("run-tests.sh", "run-python.sh", "run-xcodebuild.sh", "test-make-trust-boundary.py", "test-project-topology.py"):
        require((ROOT / "scripts" / executable).stat().st_mode & 0o111,
                f"scripts/{executable} must be executable",
                failures)

    validate_project_topology(project, app_plist, test_plist, failures)
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
            "Winner selection must return nil when no typed, nonempty participants are available",
            failures)
    motion_ended_body = swift_function_body(view_controller, "override func motionEnded")
    shake_predicate_body = swift_function_body(view_controller, "func shouldPresentWinner")
    responder_opt_in_body = swift_function_body(view_controller, "override var canBecomeFirstResponder")
    view_did_appear_body = swift_function_body(view_controller, "override func viewDidAppear")
    view_will_disappear_body = swift_function_body(view_controller, "override func viewWillDisappear")
    click_button_body = swift_function_body(view_controller, "@IBAction func clickBtn")
    present_winner_body = swift_function_body(view_controller, "func presentWinnerIfPossible")
    update_winner_action_body = swift_function_body(view_controller, "func updateWinnerActionAvailability")
    unwind_to_list_body = swift_function_body(view_controller, "@IBAction func unwindToList")
    remove_participant_body = swift_function_body(view_controller, "func removeParticipantAtIndex")
    load_initial_data_body = swift_function_body(view_controller, "func loadInitialData")
    require("func canPickWinner() -> Bool" in view_controller and
            "return !self.participantItems().isEmpty" in view_controller and
            "self.presentWinnerIfPossible()" in click_button_body and
            "self.shouldPresentWinner(for: motion)" in motion_ended_body and
            "self.presentWinnerIfPossible()" in motion_ended_body and
            "event?.subtype" not in motion_ended_body and
            "motion == .motionShake && self.canPickWinner()" in shake_predicate_body and
            "self.players.count > 0" not in view_controller,
            "button and authoritative shake-motion winner actions must require a typed, nonempty participant",
            failures)
    require("!winnerPresentationInProgress && self.canPickWinner()" in present_winner_body and
            "winnerPresentationInProgress = true" in present_winner_body and
            'self.performSegue(withIdentifier: "presentWinner", sender: self)' in present_winner_body and
            present_winner_body.find("winnerPresentationInProgress = true") < present_winner_body.find("self.performSegue") and
            "winnerPresentationInProgress = false" in view_did_appear_body and
            "testWinnerPresentationIsSingleFlightAcrossButtonAndShake" in tests and
            "RecordingWinnerPresentationViewController" in tests and
            "XCTAssertEqual(controller.performedWinnerSegueCount, 1" in tests and
            "XCTAssertEqual(controller.performedWinnerSegueCount, 2" in tests,
            "winner navigation must reserve one transition across button and shake inputs",
            failures)
    require("self.pickWinner?.isEnabled = self.canPickWinner()" in update_winner_action_body and
            "self.players.add(item)" in unwind_to_list_body and
            "self.updateWinnerActionAvailability()" in unwind_to_list_body and
            unwind_to_list_body.find("self.players.add(item)") < unwind_to_list_body.find("self.updateWinnerActionAvailability()") and
            "self.players.removeObject(at: index)" in remove_participant_body and
            "self.updateWinnerActionAvailability()" in remove_participant_body and
            remove_participant_body.find("self.players.removeObject(at: index)") < remove_participant_body.find("self.updateWinnerActionAvailability()") and
            "self.players.add(item1)" in load_initial_data_body and
            "self.updateWinnerActionAvailability()" in load_initial_data_body and
            load_initial_data_body.find("self.players.add(item1)") < load_initial_data_body.find("self.updateWinnerActionAvailability()"),
            "winner button availability must follow every production participant mutation",
            failures)
    require("return true" in responder_opt_in_body and
            "super.viewDidAppear(animated)" in view_did_appear_body and
            "becomeFirstResponder()" in view_did_appear_body and
            view_did_appear_body.find("super.viewDidAppear(animated)") < view_did_appear_body.find("becomeFirstResponder()") and
            "resignFirstResponder()" in view_will_disappear_body and
            "super.viewWillDisappear(animated)" in view_will_disappear_body and
            view_will_disappear_body.find("resignFirstResponder()") < view_will_disappear_body.find("super.viewWillDisappear(animated)") and
            "testRouletteControllerOwnsFirstResponderWhileVisible" in tests and
            "RecordingResponderViewController" in tests and
            "XCTAssertTrue(controller.canBecomeFirstResponder)" in tests and
            "XCTAssertEqual(controller.becomeFirstResponderCount, 1)" in tests and
            "XCTAssertEqual(controller.resignFirstResponderCount, 1)" in tests,
            "visible roulette lifecycle must own first-responder status for shake delivery",
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
            "func visibleName(for participantItem: ParticipantListItem) -> String?" in view_controller and
            "ParticipantListItem.normalizedName(participantItem.itemName)" in view_controller and
            "func isVisibleParticipantItem(_ participantItem: ParticipantListItem) -> Bool" in view_controller and
            "self.isVisibleParticipantItem(participantItem)" in view_controller and
            "Int.random(in: participantItems.indices)" in view_controller and
            "return self.visibleName(for: winner)" in view_controller and
            "arc4random_uniform" not in view_controller and
            "self.players.objectAtIndex(Int(randomIndex)) as!" not in view_controller,
            "Winner selection must filter the legacy player array to typed, nonempty participants before bounded random participant selection",
            failures)
    require("func participantItemAtIndex(_ index: Int) -> ParticipantListItem?" in view_controller and
            "guard let participantItem = self.players.object(at: index) as? ParticipantListItem" in view_controller and
            "self.isVisibleParticipantItem(participantItem)" in view_controller and
            "return participantItem" in view_controller,
            "Participant table rendering must use a guarded nonempty participant accessor",
            failures)
    require("func removeParticipantAtIndex(_ index: Int) -> Bool" in view_controller and
            "self.participantItemAtIndex(index) != nil" in view_controller and
            "self.players.removeObject(at: index)" in view_controller,
            "Raw participant deletion must preserve its typed, nonempty index guard",
            failures)
    visible_index_body = swift_function_body(view_controller, "func playerIndexForParticipantRow")
    visible_item_body = swift_function_body(view_controller, "func participantItemForVisibleRow")
    visible_removal_body = swift_function_body(view_controller, "func removeParticipantForVisibleRow")
    row_count_body = swift_function_body(view_controller, "numberOfRowsInSection")
    row_selection_body = swift_function_body(view_controller, "didSelectRowAt")
    require("participantRow < 0" in visible_index_body and
            "participantItemAtIndex(playerIndex) != nil" in visible_index_body and
            "visibleRow == participantRow" in visible_index_body and
            "visibleRow += 1" in visible_index_body,
            "Visible participant rows must map through typed, nonempty entries",
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
    require("unicodeScalars.contains" in participant_model and
            ".generalCategory" in participant_model and
            ".control" in participant_model and
            ".format" in participant_model,
            "Participant normalization must reject names made only from control or format scalars",
            failures)
    require("testParticipantNameNormalizationRejectsInvisibleOnlyNames" in tests and
            'normalizedName("\\u{200B}\\u{2060}")' in tests and
            'normalizedName("\\u{0000}")' in tests and
            'normalizedName("👨‍👩‍👧‍👦")' in tests,
            "XCTest must cover invisible-only names without rejecting visible joined emoji",
            failures)
    require("testParticipantNameNormalizationTrimsWhitespace" in tests and "XCTAssertEqual" in tests and
            "testParticipantNameNormalizationRejectsBlankNames" in tests and "XCTAssertNil" in tests and
            "testParticipantItemFromAddParticipantSource" in tests and
            "testParticipantItemFromWinnerSource" in tests and
            "testParticipantItemFromUnknownSourceReturnsNil" in tests and
            "testParticipantItemsIgnoreInvalidPlayerEntries" in tests and
            "testCanPickWinnerRejectsEmptyAndInvalidOnlyPlayers" in tests and
            "testCanPickWinnerAcceptsTypedParticipantAmongInvalidEntries" in tests and
            "testCanPickWinnerRejectsTypedParticipantsWithoutVisibleNames" in tests and
            "testPickAWinnerRejectsTypedParticipantsWithoutVisibleNames" in tests and
            "testWinnerButtonAvailabilityFollowsInitialLoadAndRemoval" in tests and
            "testParticipantUnwindEnablesWinnerButton" in tests and
            tests.count("controller.updateWinnerActionAvailability()") >= 2 and
            tests.count("XCTAssertFalse(controller.pickWinner.isEnabled") == 2 and
            tests.count("XCTAssertTrue(controller.pickWinner.isEnabled") == 2 and
            tests.count("XCTAssertFalse(controller.canPickWinner()") >= 3 and
            "XCTAssertTrue(controller.canPickWinner()" in tests and
            "testShakeMotionRequiresTypedParticipant" in tests and
            tests.count("controller.shouldPresentWinner(for: .motionShake)") == 3 and
            "testNonShakeMotionDoesNotPresentWinner" in tests and
            "controller.shouldPresentWinner(for: .remoteControlPlay)" in tests and
            "testParticipantItemAtIndexRejectsInvalidEntries" in tests and
            "testRemoveParticipantAtIndexRemovesValidEntry" in tests and
            "testRemoveParticipantAtIndexRejectsInvalidIndexes" in tests and
            "testRemoveParticipantAtIndexRejectsInvalidEntryType" in tests and
            "testVisibleParticipantRowsIgnoreInvalidEntries" in tests and
            "testVisibleParticipantRowsIgnoreTypedEntriesWithoutVisibleNames" in tests and
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
    for make_contract in (
        "override SHELL := /bin/sh",
        "override PYTHON := $(ROOT)/scripts/run-python.sh",
        "override XCODEBUILD := $(ROOT)/scripts/run-xcodebuild.sh",
        "MAKEFILES must be empty",
        "MAKEFLAGS must not be overridden",
        "repository Makefile must be loaded alone",
        '"$$PYTHON" "$$ROOT/scripts/check-baseline.py"',
    ):
        require(make_contract in makefile,
                f"Makefile must preserve authority contract: {make_contract}",
                failures)
    require("/usr/bin/xcrun simctl list devices available" in test_runner and
            "IOS_DESTINATION" in test_runner and "IOS_SIMULATOR_NAME" in test_runner and
            "DERIVED_DATA_PATH" in test_runner and
            '-scheme "$SCHEME"' in test_runner and '-destination "$DESTINATION"' in test_runner and
            '-derivedDataPath "$DERIVED_DATA_PATH"' in test_runner and
            "CODE_SIGNING_ALLOWED=NO" in test_runner and "test" in test_runner,
            "test runner must discover or accept a simulator, keep DerivedData configurable, and execute unsigned XCTest",
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
    require("absolute Makefile path" in readme and "any working directory" in readme,
            "README must document location-independent verification", failures)
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
    require("Make verification target derive the checkout root" in changes and "external directories" in changes,
            "CHANGES must record location-independent verification", failures)
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
    location_statuses = re.findall(r"(?mi)^status:\s*(.+?)\s*$", location_independent_make_plan)
    location_verification = markdown_section(location_independent_make_plan, "Verification Completed")
    location_required = ("Root and external-directory Make gates passed", "root-derivation mutation failed", "checker-invocation mutation failed", "XCTest-runner mutation failed", "plan-status mutation failed", "plan-evidence mutation failed", "documentation mutation failed")
    require(location_statuses == ["completed"] and all(item in location_verification for item in location_required) and not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", location_verification),
            "location-independent Make plan must record completed verification", failures)
    shake_motion_statuses = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", shake_motion_plan
    )
    shake_motion_verification = markdown_section(
        shake_motion_plan, "Verification Completed"
    )
    shake_motion_required = (
        "All four Make gates",
        "absolute Makefile check",
        "python3 -m py_compile scripts/check-baseline.py",
        "sh -n scripts/run-tests.sh",
        "Five isolated hostile mutations",
        "git diff --check",
        "xcodebuild was unavailable",
    )
    require(shake_motion_statuses == ["completed"]
            and all(item in shake_motion_verification
                    for item in shake_motion_required)
            and not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b",
                              shake_motion_verification),
            "shake motion routing plan must record completed verification",
            failures)
    normalized_guidance = [
        " ".join(document.lower().split())
        for document in [readme, vision, security, changes, read("AGENTS.md")]
    ]
    require(all("authoritative motion argument" in document and
                "typed participant" in document
                for document in normalized_guidance),
            "project guidance must document authoritative shake routing",
            failures)
    require(all("nonempty" in document for document in normalized_guidance),
            "project guidance must document nonempty participant eligibility",
            failures)
    require(all("control or format" in document for document in normalized_guidance),
            "project guidance must document invisible-only participant rejection",
            failures)
    shake_responder_statuses = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", shake_responder_plan
    )
    shake_responder_verification = markdown_section(
        shake_responder_plan, "Verification Completed"
    )
    shake_responder_required = (
        "All four Make gates",
        "absolute Makefile",
        "python3 -m py_compile scripts/check-baseline.py",
        "sh -n scripts/run-tests.sh",
        "Six isolated hostile mutations",
        "git diff --check",
        "xcodebuild was unavailable",
    )
    require(shake_responder_statuses == ["completed"]
            and all(item in shake_responder_verification
                    for item in shake_responder_required)
            and not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b",
                              shake_responder_verification),
            "shake first-responder plan must record completed verification",
            failures)
    require(all("visible first-responder ownership" in document
                for document in normalized_guidance),
            "project guidance must document visible first-responder ownership",
            failures)
    winner_single_flight_statuses = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", winner_single_flight_plan
    )
    winner_single_flight_verification = markdown_section(
        winner_single_flight_plan, "Verification Completed"
    )
    winner_single_flight_required = (
        "All four Make gates",
        "absolute Makefile",
        "python3 -m py_compile scripts/check-baseline.py",
        "sh -n scripts/run-tests.sh",
        "Seven isolated hostile mutations",
        "git diff --check",
        "xcodebuild was unavailable",
    )
    require(winner_single_flight_statuses == ["completed"]
            and all(item in winner_single_flight_verification
                    for item in winner_single_flight_required)
            and not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b",
                              winner_single_flight_verification),
            "winner single-flight plan must record completed verification",
            failures)
    require(all("single-flight winner presentation" in document
                for document in normalized_guidance),
            "project guidance must document single-flight winner presentation",
            failures)
    winner_action_availability_statuses = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", winner_action_availability_plan
    )
    winner_action_availability_verification = markdown_section(
        winner_action_availability_plan, "Verification Completed"
    )
    winner_action_availability_required = (
        "All four Make gates",
        "absolute Makefile",
        "python3 -m py_compile scripts/check-baseline.py",
        "sh -n scripts/run-tests.sh",
        "Eight isolated hostile mutations",
        "git diff --check",
        "xcodebuild was unavailable",
    )
    require(winner_action_availability_statuses == ["completed"]
            and all(item in winner_action_availability_verification
                    for item in winner_action_availability_required)
            and not re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b",
                              winner_action_availability_verification),
            "winner action availability plan must record completed verification",
            failures)
    require(all("winner action availability" in document
                for document in normalized_guidance),
            "project guidance must document winner action availability",
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

    xcodebuild = XCODEBUILD_PATH
    if xcodebuild.is_file() and os.access(xcodebuild, os.X_OK):
        result = subprocess.run(
            [
                str(xcodebuild),
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
        if result.returncode == 0:
            validate_effective_project_settings(xcodebuild, failures)
    else:
        if not failures:
            print(
                "xcodebuild unavailable; static project grammar and topology validated; "
                "effective settings not executed."
            )

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("ios-credit-card-roulette baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
