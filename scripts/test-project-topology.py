#!/usr/bin/env python3
import importlib.util
import plistlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_PATH = Path("CardRoulette.xcodeproj/project.pbxproj")
APP_DEBUG_IDENTIFIER = "\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.gpj.CardRoulette;"
SPEC = importlib.util.spec_from_file_location(
    "check_baseline", ROOT / "scripts/check-baseline.py"
)
CHECK_BASELINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_BASELINE)


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
                "reordered-app-configurations",
                lambda project: project.replace(
                    "\t\t\t\tFDAE1E8F1B1A487600A89C51 /* Debug */,\n"
                    "\t\t\t\tFDAE1E901B1A487600A89C51 /* Release */,",
                    "\t\t\t\tFDAE1E901B1A487600A89C51 /* Release */,\n"
                    "\t\t\t\tFDAE1E8F1B1A487600A89C51 /* Debug */,",
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
