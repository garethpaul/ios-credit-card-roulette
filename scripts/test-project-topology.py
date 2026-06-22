#!/usr/bin/env python3
import importlib.util
import contextlib
import io
import os
import plistlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
PROJECT_PATH = Path("CardRoulette.xcodeproj/project.pbxproj")
APP_DEBUG_IDENTIFIER = "\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.gpj.CardRoulette;"
OPENSTEP_SPEC = importlib.util.spec_from_file_location(
    "openstep_pbx", ROOT / "scripts/openstep_pbx.py"
)
OPENSTEP_PBX = importlib.util.module_from_spec(OPENSTEP_SPEC)
OPENSTEP_SPEC.loader.exec_module(OPENSTEP_PBX)
OpenStepParseError = OPENSTEP_PBX.OpenStepParseError
parse_openstep = OPENSTEP_PBX.parse_openstep
SPEC = importlib.util.spec_from_file_location(
    "check_baseline", ROOT / "scripts/check-baseline.py"
)
CHECK_BASELINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_BASELINE)


class OpenStepParserTests(unittest.TestCase):
    def test_parses_comments_quoted_escapes_nested_values_and_unicode(self):
        parsed = parse_openstep(r'''
            // !$*UTF8*$!
            {
                "na\U006de" = "Caf\U00e9 🎲";
                nested = {
                    values = (one, "tw\157", { enabled = YES; });
                };
                /* braces and assignments here are ignored: { name = decoy; } */
            }
        ''')
        self.assertEqual(parsed["name"], "Café 🎲")
        self.assertEqual(parsed["nested"]["values"], ["one", "two", {"enabled": "YES"}])

    def test_combines_unicode_surrogate_escape_pairs(self):
        parsed = parse_openstep(r'{ emoji = "\Ud83d\Ude00"; }')
        self.assertEqual(parsed["emoji"], "😀")

    def test_rejects_unpaired_unicode_surrogate_escapes(self):
        for fixture in (r'{ key = "\Ud83d"; }', r'{ key = "\Ude00"; }'):
            with self.subTest(fixture=fixture):
                with self.assertRaises(OpenStepParseError):
                    parse_openstep(fixture)

    def test_rejects_duplicate_normalized_keys(self):
        with self.assertRaises(OpenStepParseError):
            parse_openstep(r'{ name = CardRoulette; "na\U006de" = Legacy; }')

    def test_rejects_duplicate_object_uuids(self):
        with self.assertRaises(OpenStepParseError):
            parse_openstep('''{
                objects = {
                    AAAAAAAAAAAAAAAAAAAAAAAA = { isa = PBXNativeTarget; };
                    "AAAAAAAAAAAAAAAAAAAAAAAA" = { isa = PBXFileReference; };
                };
            }''')

    def test_rejects_unterminated_comments_and_containers(self):
        for fixture in ("{ key = value; /*", "{ key = (value, );", '{ key = "value; }'):
            with self.subTest(fixture=fixture):
                with self.assertRaises(OpenStepParseError):
                    parse_openstep(fixture)

    def test_rejects_apostrophe_quoted_strings(self):
        for fixture in (
            "{ 'name' = CardRoulette; }",
            "{ name = 'CardRoulette'; }",
        ):
            with self.subTest(fixture=fixture):
                with self.assertRaises(OpenStepParseError):
                    parse_openstep(fixture)

    def test_rejects_invalid_bare_token_characters(self):
        for token in ("@odd", "name#fragment", "value\\escape"):
            with self.subTest(token=token):
                with self.assertRaises(OpenStepParseError):
                    parse_openstep("{ metadata = " + token + "; }")


class XcodeBuildSettingsParserTests(unittest.TestCase):
    def test_ignores_unrelated_duplicate_rows_when_expected_settings_are_unique(self):
        output = """\
    SDKROOT = iphonesimulator26.0
    PRODUCT_BUNDLE_IDENTIFIER = com.gpj.CardRoulette
    SDKROOT = /Applications/Xcode.app/iPhoneSimulator.sdk
"""
        self.assertEqual(
            CHECK_BASELINE.parse_xcodebuild_settings(
                output, {"PRODUCT_BUNDLE_IDENTIFIER"}
            ),
            {"PRODUCT_BUNDLE_IDENTIFIER": "com.gpj.CardRoulette"},
        )

    def test_rejects_conflicting_expected_setting_rows(self):
        output = """\
    PRODUCT_BUNDLE_IDENTIFIER = com.gpj.CardRoulette
    PRODUCT_BUNDLE_IDENTIFIER = com.attacker.CardRoulette
"""
        with self.assertRaises(ValueError):
            CHECK_BASELINE.parse_xcodebuild_settings(
                output, {"PRODUCT_BUNDLE_IDENTIFIER"}
            )


class ProjectTopologyTests(unittest.TestCase):
    def run_mutation(
        self,
        mutate=lambda project: project,
        expected_success=False,
        mutate_app_plist=None,
        mutate_test_plist=None,
    ):
        project = (ROOT / PROJECT_PATH).read_text(encoding="utf-8")
        mutated = mutate(project)
        with (ROOT / "CardRoulette/Info.plist").open("rb") as file:
            app_plist = plistlib.load(file)
        with (ROOT / "CardRouletteTests/Info.plist").open("rb") as file:
            test_plist = plistlib.load(file)
        if mutate_app_plist:
            app_plist = mutate_app_plist(dict(app_plist))
        if mutate_test_plist:
            test_plist = mutate_test_plist(dict(test_plist))
        self.assertTrue(
            project != mutated or mutate_app_plist or mutate_test_plist,
            "mutation must change the project or a plist",
        )
        failures = []
        CHECK_BASELINE.validate_project_topology(
            mutated, app_plist, test_plist, failures
        )
        if expected_success:
            self.assertEqual(failures, [])
        else:
            self.assertNotEqual(failures, [])

    def test_rejects_identifier_present_only_in_block_comment(self):
        self.run_mutation(lambda project: project.replace(
            APP_DEBUG_IDENTIFIER,
            "\t\t\t\t/*\n" + APP_DEBUG_IDENTIFIER + "\n\t\t\t\t*/",
            1,
        ))

    def test_rejects_identifier_present_only_in_line_comment(self):
        self.run_mutation(lambda project: project.replace(
            APP_DEBUG_IDENTIFIER,
            "\t\t\t\t// PRODUCT_BUNDLE_IDENTIFIER = com.gpj.CardRoulette;",
            1,
        ))

    def test_accepts_adjacent_block_comment_identifier_decoy(self):
        self.run_mutation(lambda project: project.replace(
            APP_DEBUG_IDENTIFIER,
            "\t\t\t\t/* { PRODUCT_BUNDLE_IDENTIFIER = com.example.Decoy; } */\n"
            + APP_DEBUG_IDENTIFIER,
            1,
        ), expected_success=True)

    def test_accepts_trailing_line_comment_identifier_decoy(self):
        self.run_mutation(lambda project: project.replace(
            APP_DEBUG_IDENTIFIER,
            APP_DEBUG_IDENTIFIER + " // PRODUCT_BUNDLE_IDENTIFIER = com.example.Decoy;",
            1,
        ), expected_success=True)

    def test_accepts_reordered_native_target_objects(self):
        def mutate(project):
            app_start = project.index(
                "\t\tFDAE1E6E1B1A487600A89C51 /* CardRoulette */ = {"
            )
            test_start = project.index(
                "\t\tFDAE1E831B1A487600A89C51 /* CardRouletteTests */ = {"
            )
            section_end = project.index("/* End PBXNativeTarget section */")
            app_block = project[app_start:test_start]
            test_block = project[test_start:section_end]
            return project[:app_start] + test_block + app_block + project[section_end:]

        self.run_mutation(mutate, expected_success=True)

    def test_accepts_reordered_root_target_membership(self):
        self.run_mutation(lambda project: project.replace(
            "\t\t\t\tFDAE1E6E1B1A487600A89C51 /* CardRoulette */,\n"
            "\t\t\t\tFDAE1E831B1A487600A89C51 /* CardRouletteTests */,",
            "\t\t\t\tFDAE1E831B1A487600A89C51 /* CardRouletteTests */,\n"
            "\t\t\t\tFDAE1E6E1B1A487600A89C51 /* CardRoulette */,",
            1,
        ), expected_success=True)

    def test_rejects_missing_extra_or_duplicate_root_target_membership(self):
        target_rows = (
            "\t\t\t\tFDAE1E6E1B1A487600A89C51 /* CardRoulette */,\n"
            "\t\t\t\tFDAE1E831B1A487600A89C51 /* CardRouletteTests */,"
        )
        mutations = {
            "missing": "\t\t\t\tFDAE1E6E1B1A487600A89C51 /* CardRoulette */ ,",
            "extra": target_rows + "\n\t\t\t\tAAAAAAAAAAAAAAAAAAAAAAAA /* Extra */,",
            "duplicate": (
                "\t\t\t\tFDAE1E6E1B1A487600A89C51 /* CardRoulette */,\n"
                "\t\t\t\tFDAE1E6E1B1A487600A89C51 /* CardRoulette duplicate */,"
            ),
            "nested-array": (
                "\t\t\t\t(FDAE1E6E1B1A487600A89C51),\n"
                "\t\t\t\tFDAE1E831B1A487600A89C51 /* CardRouletteTests */,"
            ),
            "nested-dictionary": (
                "\t\t\t\t{ target = FDAE1E6E1B1A487600A89C51; },\n"
                "\t\t\t\tFDAE1E831B1A487600A89C51 /* CardRouletteTests */,"
            ),
        }
        for name, replacement in mutations.items():
            with self.subTest(name=name):
                self.run_mutation(
                    lambda project, replacement=replacement: project.replace(
                        target_rows, replacement, 1
                    )
                )

    def test_accepts_supported_canonical_object_versions(self):
        for version in (42, 46, 77, 90):
            if version == 46:
                continue
            with self.subTest(version=version):
                self.run_mutation(lambda project, version=version: project.replace(
                    "objectVersion = 46;", f"objectVersion = {version};", 1
                ), expected_success=True)

    def test_rejects_invalid_top_level_project_schema(self):
        mutations = {
            "missing-archive-version": lambda project: project.replace(
                "\tarchiveVersion = 1;\n", "", 1
            ),
            "wrong-archive-version": lambda project: project.replace(
                "archiveVersion = 1;", "archiveVersion = 2;", 1
            ),
            "nonnumeric-archive-version": lambda project: project.replace(
                "archiveVersion = 1;", "archiveVersion = nonsense;", 1
            ),
            "quoted-archive-version": lambda project: project.replace(
                "archiveVersion = 1;", 'archiveVersion = "1";', 1
            ),
            "missing-object-version": lambda project: project.replace(
                "\tobjectVersion = 46;\n", "", 1
            ),
            "nonnumeric-object-version": lambda project: project.replace(
                "objectVersion = 46;", "objectVersion = nonsense;", 1
            ),
            "duplicate-object-version": lambda project: project.replace(
                "objectVersion = 46;",
                "objectVersion = 46;\n\tobjectVersion = 46;",
                1,
            ),
            "quoted-object-version": lambda project: project.replace(
                "objectVersion = 46;", 'objectVersion = "46";', 1
            ),
            "leading-zero-object-version": lambda project: project.replace(
                "objectVersion = 46;", "objectVersion = 046;", 1
            ),
            "fractional-object-version": lambda project: project.replace(
                "objectVersion = 46;", "objectVersion = 46.0;", 1
            ),
            "unsupported-low-object-version": lambda project: project.replace(
                "objectVersion = 46;", "objectVersion = 41;", 1
            ),
            "unsupported-high-object-version": lambda project: project.replace(
                "objectVersion = 46;", "objectVersion = 91;", 1
            ),
            "oversized-object-version": lambda project: project.replace(
                "objectVersion = 46;", "objectVersion = " + ("9" * 5000) + ";", 1
            ),
            "missing-classes": lambda project: project.replace(
                "\tclasses = {\n\t};\n", "", 1
            ),
            "nondictionary-classes": lambda project: project.replace(
                "\tclasses = {\n\t};", "\tclasses = ();", 1
            ),
            "missing-objects": lambda project: project.replace(
                "\tobjects = {", "\tprojectObjects = {", 1
            ),
            "nondictionary-objects": lambda project: project.replace(
                "\tobjects = {", "\tobjects = (\n\t\t{", 1
            ).replace(
                "\n\t};\n\trootObject = FDAE1E671B1A487600A89C51",
                "\n\t\t}\n\t);\n\trootObject = FDAE1E671B1A487600A89C51",
                1,
            ),
            "missing-root-object": lambda project: project.replace(
                "\trootObject = FDAE1E671B1A487600A89C51 /* Project object */;\n",
                "",
                1,
            ),
            "quoted-root-object": lambda project: project.replace(
                "rootObject = FDAE1E671B1A487600A89C51",
                'rootObject = "FDAE1E671B1A487600A89C51"',
                1,
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                self.run_mutation(mutate)

    def test_accepts_reordered_configuration_objects_and_lists(self):
        def mutate(project):
            app_debug_start = project.index(
                "\t\tFDAE1E8F1B1A487600A89C51 /* Debug */ = {"
            )
            app_release_start = project.index(
                "\t\tFDAE1E901B1A487600A89C51 /* Release */ = {"
            )
            test_debug_start = project.index(
                "\t\tFDAE1E921B1A487600A89C51 /* Debug */ = {"
            )
            test_release_start = project.index(
                "\t\tFDAE1E931B1A487600A89C51 /* Release */ = {"
            )
            section_end = project.index("/* End XCBuildConfiguration section */")
            app_debug = project[app_debug_start:app_release_start]
            app_release = project[app_release_start:test_debug_start]
            test_debug = project[test_debug_start:test_release_start]
            test_release = project[test_release_start:section_end]
            project = (
                project[:app_debug_start]
                + test_release
                + app_release
                + test_debug
                + app_debug
                + project[section_end:]
            )
            project = project.replace(
                "\t\t\t\tFDAE1E8F1B1A487600A89C51 /* Debug */,\n"
                "\t\t\t\tFDAE1E901B1A487600A89C51 /* Release */,",
                "\t\t\t\tFDAE1E901B1A487600A89C51 /* Release */,\n"
                "\t\t\t\tFDAE1E8F1B1A487600A89C51 /* Debug */,",
                1,
            )
            return project.replace(
                "\t\t\t\tFDAE1E921B1A487600A89C51 /* Debug */,\n"
                "\t\t\t\tFDAE1E931B1A487600A89C51 /* Release */,",
                "\t\t\t\tFDAE1E931B1A487600A89C51 /* Release */,\n"
                "\t\t\t\tFDAE1E921B1A487600A89C51 /* Debug */,",
                1,
            )

        self.run_mutation(mutate, expected_success=True)

    def test_rejects_duplicate_configuration_list_members(self):
        self.run_mutation(lambda project: project.replace(
            "\t\t\t\tFDAE1E901B1A487600A89C51 /* Release */,",
            "\t\t\t\tFDAE1E8F1B1A487600A89C51 /* Debug */,",
            1,
        ))

    def test_rejects_conditional_bundle_identifier_variants(self):
        app_identifier = "PRODUCT_BUNDLE_IDENTIFIER = com.gpj.CardRoulette;"
        test_identifier = "PRODUCT_BUNDLE_IDENTIFIER = com.gpj.CardRouletteTests;"
        conditions = (
            "sdk=iphonesimulator*",
            "platform=iphonesimulator",
            "arch=*",
            "config=Debug",
        )
        for identifier, value in (
            (app_identifier, "com.attacker.CardRoulette"),
            (test_identifier, "com.attacker.CardRouletteTests"),
        ):
            for occurrence in (1, 2):
                for condition in conditions:
                    with self.subTest(
                        identifier=identifier,
                        occurrence=occurrence,
                        condition=condition,
                    ):
                        qualified = (
                            f'"PRODUCT_BUNDLE_IDENTIFIER[{condition}]" = {value};'
                        )
                        self.run_mutation(
                            lambda project, identifier=identifier,
                            occurrence=occurrence, qualified=qualified:
                            replace_occurrence(
                                project,
                                identifier,
                                identifier + "\n\t\t\t\t" + qualified,
                                occurrence,
                            )
                        )

    def test_no_xcode_static_gate_rejects_invalid_project_grammar(self):
        project = (ROOT / PROJECT_PATH).read_text(encoding="utf-8").replace(
            "\tclasses = {\n\t};",
            "\tclasses = {\n\t\tmetadata = @odd;\n\t};",
            1,
        )
        original_read = CHECK_BASELINE.read

        def read_with_invalid_project(relative_path):
            if relative_path == str(PROJECT_PATH):
                return project
            return original_read(relative_path)

        stdout = io.StringIO()
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as empty_path:
            with mock.patch.object(CHECK_BASELINE, "read", read_with_invalid_project), \
                    mock.patch.object(
                        CHECK_BASELINE,
                        "XCODEBUILD_PATH",
                        Path(empty_path) / "missing-xcodebuild",
                        create=True,
                    ), \
                    mock.patch.object(CHECK_BASELINE.subprocess, "check_call"), \
                    mock.patch.dict(os.environ, {"PATH": empty_path}, clear=False), \
                    contextlib.redirect_stdout(stdout), \
                    contextlib.redirect_stderr(stderr):
                result = CHECK_BASELINE.main()

        self.assertEqual(result, 1)
        self.assertIn("Xcode project must be valid OpenStep syntax", stderr.getvalue())
        self.assertNotIn("effective settings validated", stdout.getvalue())

    def test_no_xcode_static_gate_rejects_invalid_project_schema(self):
        project = (ROOT / PROJECT_PATH).read_text(encoding="utf-8").replace(
            "objectVersion = 46;",
            "objectVersion = nonsense;",
            1,
        )
        original_read = CHECK_BASELINE.read

        def read_with_invalid_project(relative_path):
            if relative_path == str(PROJECT_PATH):
                return project
            return original_read(relative_path)

        stdout = io.StringIO()
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as empty_path:
            with mock.patch.object(CHECK_BASELINE, "read", read_with_invalid_project), \
                    mock.patch.object(
                        CHECK_BASELINE,
                        "XCODEBUILD_PATH",
                        Path(empty_path) / "missing-xcodebuild",
                        create=True,
                    ), \
                    mock.patch.object(CHECK_BASELINE.subprocess, "check_call"), \
                    mock.patch.dict(os.environ, {"PATH": empty_path}, clear=False), \
                    contextlib.redirect_stdout(stdout), \
                    contextlib.redirect_stderr(stderr):
                result = CHECK_BASELINE.main()

        self.assertEqual(result, 1)
        self.assertIn(
            "objectVersion must be a canonical supported integer",
            stderr.getvalue(),
        )
        self.assertNotIn("static project grammar and topology validated", stdout.getvalue())
        self.assertNotIn("effective settings validated", stdout.getvalue())

    def test_no_xcode_static_gate_reports_exact_environment_boundary(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as empty_path:
            with mock.patch.object(
                    CHECK_BASELINE,
                    "XCODEBUILD_PATH",
                    Path(empty_path) / "missing-xcodebuild",
                    create=True,
                ), mock.patch.object(CHECK_BASELINE.subprocess, "check_call"), \
                    mock.patch.dict(os.environ, {"PATH": empty_path}, clear=False), \
                    contextlib.redirect_stdout(stdout), \
                    contextlib.redirect_stderr(stderr):
                result = CHECK_BASELINE.main()

        self.assertEqual(result, 0, stderr.getvalue())
        self.assertIn(
            "xcodebuild unavailable; static project grammar and topology validated; "
            "effective settings not executed.",
            stdout.getvalue(),
        )

    def test_accepts_unicode_and_nested_nonidentity_metadata(self):
        self.run_mutation(lambda project: project.replace(
            "\tclasses = {\n\t};",
            '\tclasses = {\n\t\tmetadata = { label = "Café 🎲"; };\n\t};',
            1,
        ), expected_success=True)

    def test_rejects_app_target_rename(self):
        self.run_mutation(lambda project: project.replace(
            "\t\t\tname = CardRoulette;",
            "\t\t\tname = CardRouletteLegacy;",
            1,
        ))

    def test_rejects_test_target_rename(self):
        self.run_mutation(lambda project: project.replace(
            "\t\t\tname = CardRouletteTests;",
            "\t\t\tname = CardRouletteLegacyTests;",
            1,
        ))

    def test_rejects_app_product_name_change(self):
        self.run_mutation(lambda project: project.replace(
            "\t\t\tproductName = CardRoulette;",
            "\t\t\tproductName = CardRouletteLegacy;",
            1,
        ))

    def test_rejects_test_product_name_change(self):
        self.run_mutation(lambda project: project.replace(
            "\t\t\tproductName = CardRouletteTests;",
            "\t\t\tproductName = CardRouletteLegacyTests;",
            1,
        ))

    def test_rejects_quoted_bundle_identifier_with_nested_decoy(self):
        def mutate(project):
            project = project.replace(
                APP_DEBUG_IDENTIFIER,
                '\t\t\t\t"PRODUCT_BUNDLE_IDENTIFIER" = com.attacker.CardRoulette;',
                1,
            )
            configuration_end = project.index(
                "\t\t\t};\n\t\t\tname = Debug;",
                project.index('"PRODUCT_BUNDLE_IDENTIFIER"'),
            )
            return project[:configuration_end + len("\t\t\t};")] + (
                "\n\t\t\tdecoyIdentity = {\n"
                "\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.gpj.CardRoulette;\n"
                "\t\t\t};"
            ) + project[configuration_end + len("\t\t\t};"):]

        self.run_mutation(mutate)

    def test_rejects_quoted_target_name_with_nested_decoy(self):
        self.run_mutation(lambda project: project.replace(
            "\t\t\tname = CardRoulette;",
            '\t\t\t"name" = CardRouletteLegacy;\n'
            "\t\t\tdecoyIdentity = {\n"
            "\t\t\t\tname = CardRoulette;\n"
            "\t\t\t};",
            1,
        ))

    def test_rejects_escaped_target_name_with_nested_decoy(self):
        self.run_mutation(lambda project: project.replace(
            "\t\t\tname = CardRoulette;",
            '\t\t\t"na\\U006de" = CardRouletteLegacy;\n'
            "\t\t\tdecoyIdentity = {\n"
            "\t\t\t\tname = CardRoulette;\n"
            "\t\t\t};",
            1,
        ))

    def test_rejects_duplicate_escaped_key_in_target(self):
        self.run_mutation(lambda project: project.replace(
            "\t\t\tname = CardRoulette;",
            "\t\t\tname = CardRoulette;\n"
            '\t\t\t"na\\U006de" = CardRouletteLegacy;',
            1,
        ))

    def test_rejects_duplicate_quoted_object_uuid(self):
        self.run_mutation(lambda project: project.replace(
            "\t\tFDAE1E6E1B1A487600A89C51 /* CardRoulette */ = {",
            '\t\t"FDAE1E6E1B1A487600A89C51" = { isa = PBXFileReference; };\n'
            "\t\tFDAE1E6E1B1A487600A89C51 /* CardRoulette */ = {",
            1,
        ))

    def test_rejects_nested_identity_decoys_across_topology(self):
        cases = (
            (
                "product-name",
                "\t\t\tproductName = CardRoulette;",
                '\t\t\t"productName" = CardRouletteLegacy;\n'
                "\t\t\tdecoy = { productName = CardRoulette; };",
            ),
            (
                "configuration-list-owner",
                "\t\t\tbuildConfigurationList = FDAE1E8E1B1A487600A89C51 "
                '/* Build configuration list for PBXNativeTarget "CardRoulette" */;',
                '\t\t\t"buildConfigurationList" = FDAE1E911B1A487600A89C51;\n'
                "\t\t\tdecoy = { buildConfigurationList = FDAE1E8E1B1A487600A89C51; };",
            ),
            (
                "product-reference",
                "\t\t\tproductReference = FDAE1E6F1B1A487600A89C51 /* CardRoulette.app */;",
                '\t\t\t"productReference" = FDAE1E841B1A487600A89C51;\n'
                "\t\t\tdecoy = { productReference = FDAE1E6F1B1A487600A89C51; };",
            ),
            (
                "product-type",
                '\t\t\tproductType = "com.apple.product-type.application";',
                '\t\t\t"productType" = "com.apple.product-type.bundle.unit-test";\n'
                '\t\t\tdecoy = { productType = "com.apple.product-type.application"; };',
            ),
            (
                "product-file-type",
                "explicitFileType = wrapper.application;",
                '"explicitFileType" = wrapper.cfbundle; '
                "decoy = { explicitFileType = wrapper.application; };",
            ),
            (
                "product-path",
                "path = CardRoulette.app;",
                '"path" = CardRouletteLegacy.app; '
                "decoy = { path = CardRoulette.app; };",
            ),
            (
                "product-source-tree",
                "sourceTree = BUILT_PRODUCTS_DIR;",
                '"sourceTree" = SOURCE_ROOT; '
                "decoy = { sourceTree = BUILT_PRODUCTS_DIR; };",
            ),
            (
                "configuration-membership",
                "\t\t\tbuildConfigurations = (\n"
                "\t\t\t\tFDAE1E8F1B1A487600A89C51 /* Debug */,\n"
                "\t\t\t\tFDAE1E901B1A487600A89C51 /* Release */,\n"
                "\t\t\t);",
                '\t\t\t"buildConfigurations" = (\n'
                "\t\t\t\tFDAE1E921B1A487600A89C51,\n"
                "\t\t\t\tFDAE1E931B1A487600A89C51,\n"
                "\t\t\t);\n"
                "\t\t\tdecoy = { buildConfigurations = (\n"
                "\t\t\t\tFDAE1E8F1B1A487600A89C51,\n"
                "\t\t\t\tFDAE1E901B1A487600A89C51,\n"
                "\t\t\t); };",
            ),
            (
                "configuration-name",
                "\t\t\tname = Debug;",
                '\t\t\t"name" = Development;\n'
                "\t\t\tdecoy = { name = Debug; };",
                2,
            ),
            (
                "plist-path",
                "\t\t\t\tINFOPLIST_FILE = CardRoulette/Info.plist;",
                '\t\t\t\t"INFOPLIST_FILE" = CardRouletteTests/Info.plist;\n'
                "\t\t\t\tdecoy = { INFOPLIST_FILE = CardRoulette/Info.plist; };",
            ),
            (
                "product-name-setting",
                '\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";',
                '\t\t\t\t"PRODUCT_NAME" = CardRouletteLegacy;\n'
                '\t\t\t\tdecoy = { PRODUCT_NAME = "$(TARGET_NAME)"; };',
            ),
        )
        for case in cases:
            name, original, replacement = case[:3]
            occurrence = case[3] if len(case) == 4 else 1
            with self.subTest(name=name):
                self.run_mutation(
                    lambda project, original=original, replacement=replacement,
                    occurrence=occurrence: replace_occurrence(
                        project, original, replacement, occurrence
                    )
                )

    def test_rejects_similarly_named_decoy_target(self):
        def mutate(project):
            exact = "FDAE1E6E1B1A487600A89C51 /* CardRoulette */ = {"
            renamed = "FDAE1E6E1B1A487600A89C51 /* CardRouletteLegacy */ = {"
            decoy = "\t\t" + project[
                project.index(exact):project.index("\n\t\t};", project.index(exact)) + 5
            ]
            decoy = decoy.replace("FDAE1E6E1B1A487600A89C51", "AAAAAAAAAAAAAAAAAAAAAAAA")
            return project.replace(exact, renamed, 1).replace(
                "/* End PBXNativeTarget section */",
                decoy + "\n/* End PBXNativeTarget section */",
                1,
            ).replace(
                "\t\t\t\tFDAE1E6E1B1A487600A89C51 /* CardRoulette */,",
                "\t\t\t\tFDAE1E6E1B1A487600A89C51 /* CardRouletteLegacy */,\n"
                "\t\t\t\tAAAAAAAAAAAAAAAAAAAAAAAA /* CardRoulette */ ,",
                1,
            )

        self.run_mutation(mutate)

    def test_rejects_app_product_reference_rewire(self):
        self.run_mutation(lambda project: project.replace(
            "productReference = FDAE1E6F1B1A487600A89C51 /* CardRoulette.app */;",
            "productReference = FDAE1E841B1A487600A89C51 /* CardRouletteTests.xctest */;",
            1,
        ))

    def test_rejects_test_product_reference_rewire(self):
        self.run_mutation(lambda project: project.replace(
            "productReference = FDAE1E841B1A487600A89C51 /* CardRouletteTests.xctest */;",
            "productReference = FDAE1E6F1B1A487600A89C51 /* CardRoulette.app */;",
            1,
        ))

    def test_rejects_target_uuid_rewire(self):
        self.run_mutation(lambda project: project.replace(
            "FDAE1E6E1B1A487600A89C51",
            "AAAAAAAAAAAAAAAAAAAAAAAA",
        ))

    def test_rejects_product_uuid_rewire(self):
        self.run_mutation(lambda project: project.replace(
            "FDAE1E6F1B1A487600A89C51",
            "AAAAAAAAAAAAAAAAAAAAAAAA",
        ))

    def test_rejects_prior_identifier_and_topology_mutations(self):
        app_identifier = "PRODUCT_BUNDLE_IDENTIFIER = com.gpj.CardRoulette;"
        test_identifier = "PRODUCT_BUNDLE_IDENTIFIER = com.gpj.CardRouletteTests;"
        cases = []
        for occurrence, label in ((1, "debug"), (2, "release")):
            cases.extend((
                (
                    "wrong-app-" + label,
                    lambda project, occurrence=occurrence: replace_occurrence(
                        project, app_identifier,
                        "PRODUCT_BUNDLE_IDENTIFIER = com.example.CardRoulette;",
                        occurrence,
                    ),
                ),
                (
                    "missing-app-" + label,
                    lambda project, occurrence=occurrence: replace_occurrence(
                        project, app_identifier, "", occurrence
                    ),
                ),
                (
                    "duplicate-app-" + label,
                    lambda project, occurrence=occurrence: replace_occurrence(
                        project, app_identifier,
                        app_identifier + "\n\t\t\t\t" + app_identifier,
                        occurrence,
                    ),
                ),
                (
                    "wrong-test-" + label,
                    lambda project, occurrence=occurrence: replace_occurrence(
                        project, test_identifier,
                        "PRODUCT_BUNDLE_IDENTIFIER = com.example.CardRouletteTests;",
                        occurrence,
                    ),
                ),
                (
                    "missing-test-" + label,
                    lambda project, occurrence=occurrence: replace_occurrence(
                        project, test_identifier, "", occurrence
                    ),
                ),
                (
                    "duplicate-test-" + label,
                    lambda project, occurrence=occurrence: replace_occurrence(
                        project, test_identifier,
                        test_identifier + "\n\t\t\t\t" + test_identifier,
                        occurrence,
                    ),
                ),
            ))
        cases.extend((
            (
                "project-level-app-identifier",
                lambda project: project.replace(app_identifier, "", 1).replace(
                    "CLANG_ENABLE_MODULES = YES;",
                    "CLANG_ENABLE_MODULES = YES;\n\t\t\t\t" + app_identifier,
                    1,
                ),
            ),
            (
                "quoted-app-identifier",
                lambda project: project.replace(
                    app_identifier,
                    'PRODUCT_BUNDLE_IDENTIFIER = "com.gpj.CardRoulette";',
                    1,
                ),
            ),
            (
                "quoted-test-identifier",
                lambda project: project.replace(
                    test_identifier,
                    'PRODUCT_BUNDLE_IDENTIFIER = "com.gpj.CardRouletteTests";',
                    1,
                ),
            ),
            (
                "rewired-app-configuration",
                lambda project: project.replace(
                    "FDAE1E8F1B1A487600A89C51 /* Debug */",
                    "FDAE1E921B1A487600A89C51 /* Debug */",
                    1,
                ),
            ),
            (
                "rewired-app-configuration-list",
                lambda project: project.replace(
                    "buildConfigurationList = FDAE1E8E1B1A487600A89C51 "
                    "/* Build configuration list for PBXNativeTarget \"CardRoulette\" */;",
                    "buildConfigurationList = FDAE1E911B1A487600A89C51 "
                    "/* Build configuration list for PBXNativeTarget \"CardRouletteTests\" */;",
                    1,
                ),
            ),
            (
                "rewired-test-configuration",
                lambda project: project.replace(
                    "FDAE1E921B1A487600A89C51 /* Debug */",
                    "FDAE1E8F1B1A487600A89C51 /* Debug */",
                    1,
                ),
            ),
            (
                "rewired-test-configuration-list",
                lambda project: project.replace(
                    "buildConfigurationList = FDAE1E911B1A487600A89C51 "
                    "/* Build configuration list for PBXNativeTarget \"CardRouletteTests\" */;",
                    "buildConfigurationList = FDAE1E8E1B1A487600A89C51 "
                    "/* Build configuration list for PBXNativeTarget \"CardRoulette\" */;",
                    1,
                ),
            ),
            (
                "renamed-app-debug-configuration",
                lambda project: replace_occurrence(
                    project, "\t\t\tname = Debug;", "\t\t\tname = Development;", 2
                ),
            ),
            (
                "renamed-test-release-configuration",
                lambda project: replace_occurrence(
                    project, "\t\t\tname = Release;", "\t\t\tname = Production;", 3
                ),
            ),
            (
                "duplicate-app-debug-configuration-object",
                lambda project: project.replace(
                    "\t\tFDAE1E8F1B1A487600A89C51 /* Debug */ = {",
                    "\t\tFDAE1E8F1B1A487600A89C51 /* Debug */ = {\n"
                    "\t\t};\n"
                    "\t\tFDAE1E8F1B1A487600A89C51 /* Debug */ = {",
                    1,
                ),
            ),
            (
                "similarly-named-app-configuration",
                lambda project: project.replace(
                    "\t\t\t\tFDAE1E8F1B1A487600A89C51 /* Debug */,",
                    "\t\t\t\tAAAAAAAAAAAAAAAAAAAAAAAA /* DebugCardRoulette */,\n"
                    "\t\t\t\tFDAE1E8F1B1A487600A89C51 /* Debug */,",
                    1,
                ),
            ),
        ))
        self.assertGreaterEqual(len(cases), 23)
        for name, mutate in cases:
            with self.subTest(name=name):
                self.run_mutation(mutate)

    def test_rejects_prior_plist_mutations(self):
        def app_template(plist):
            plist["CFBundleIdentifier"] = "com.gpj.CardRoulette"
            return plist

        def test_template(plist):
            plist["CFBundleIdentifier"] = "com.gpj.CardRouletteTests"
            return plist

        def app_type(plist):
            plist["CFBundlePackageType"] = "BNDL"
            return plist

        def test_type(plist):
            plist["CFBundlePackageType"] = "APPL"
            return plist

        for name, argument, mutate in (
            ("app-plist-template", "mutate_app_plist", app_template),
            ("test-plist-template", "mutate_test_plist", test_template),
            ("app-plist-type", "mutate_app_plist", app_type),
            ("test-plist-type", "mutate_test_plist", test_type),
        ):
            with self.subTest(name=name):
                self.run_mutation(**{argument: mutate})


def replace_occurrence(text, old, new, occurrence):
    start = -1
    for _ in range(occurrence):
        start = text.find(old, start + 1)
        if start == -1:
            raise AssertionError(f"missing occurrence {occurrence}: {old}")
    return text[:start] + new + text[start + len(old):]


if __name__ == "__main__":
    unittest.main()
