#!/usr/bin/env python3
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SYSTEM_MAKE = Path("/usr/bin/make")


class MakeTrustBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary_directory = tempfile.TemporaryDirectory(
            prefix="card-roulette-make-boundary-"
        )
        cls.fixture_root = Path(cls.temporary_directory.name)
        cls.repository = cls.fixture_root / "repository with spaces"
        cls.repository_link = cls.fixture_root / "repository-link"
        cls.external_directory = cls.fixture_root / "external working directory"
        cls.fake_bin = cls.fixture_root / "fake-bin"
        cls.repository_scripts = cls.repository / "scripts"
        cls.repository_scripts.mkdir(parents=True)
        cls.repository_link.symlink_to(cls.repository, target_is_directory=True)
        cls.external_directory.mkdir()
        cls.fake_bin.mkdir()
        shutil.copy2(ROOT / "Makefile", cls.repository / "Makefile")

        cls.baseline_marker = cls.fixture_root / "baseline.marker"
        cls.native_marker = cls.fixture_root / "native.marker"
        cls.root_test_marker = cls.fixture_root / "root-test.marker"
        cls.fake_shell_marker = cls.fixture_root / "fake-shell.marker"
        cls.fake_python_marker = cls.fixture_root / "fake-python.marker"
        cls.fake_xcode_marker = cls.fixture_root / "fake-xcode.marker"
        cls.fake_root_marker = cls.fixture_root / "fake-root.marker"
        cls.replacement_marker = cls.fixture_root / "replacement.marker"
        cls.append_marker = cls.fixture_root / "append.marker"
        cls.startup_marker = cls.fixture_root / "startup.marker"
        cls.hostile_marker = cls.fixture_root / "hostile.marker"

        cls.write_executable(
            cls.repository_scripts / "run-python.sh",
            "#!/bin/sh\nexec " + cls.shell_quote(Path(sys.executable)) + ' -I -B "$@"\n',
        )
        cls.write_executable(
            cls.repository_scripts / "run-xcodebuild.sh",
            "#!/bin/sh\n"
            "if [ \"${1:-}\" = --available ]; then exit 0; fi\n"
            f"printf '%s\\n' native > {cls.shell_quote(cls.native_marker)}\n",
        )
        cls.write_executable(
            cls.repository_scripts / "check-baseline.py",
            "#!/usr/bin/env python3\n"
            "from pathlib import Path\n"
            f"Path({str(cls.baseline_marker)!r}).write_text('baseline\\n')\n",
        )
        cls.write_executable(
            cls.repository_scripts / "test-make-trust-boundary.py",
            "#!/usr/bin/env python3\n"
            "from pathlib import Path\n"
            f"Path({str(cls.root_test_marker)!r}).write_text('root-test\\n')\n",
        )
        cls.write_executable(
            cls.repository_scripts / "test-project-topology.py",
            "#!/usr/bin/env python3\n",
        )
        cls.write_executable(
            cls.repository_scripts / "run-tests.sh",
            "#!/bin/sh\nset -eu\n\"$XCODEBUILD\" -project CardRoulette.xcodeproj test\n",
        )
        cls.write_executable(
            cls.fake_bin / "python3",
            "#!/bin/sh\n"
            f"printf '%s\\n' fake-python > {cls.shell_quote(cls.fake_python_marker)}\n"
            "exit 0\n",
        )
        cls.write_executable(
            cls.fake_bin / "xcodebuild",
            "#!/bin/sh\n"
            f"printf '%s\\n' fake-xcode > {cls.shell_quote(cls.fake_xcode_marker)}\n"
            "exit 0\n",
        )
        cls.fake_shell = cls.fixture_root / "fake-shell"
        cls.write_executable(
            cls.fake_shell,
            "#!/bin/sh\n"
            f"printf '%s\\n' fake-shell > {cls.shell_quote(cls.fake_shell_marker)}\n"
            "exit 0\n",
        )

        cls.fake_root = cls.fixture_root / "fake-root"
        (cls.fake_root / "scripts").mkdir(parents=True)
        cls.write_executable(
            cls.fake_root / "scripts" / "check-baseline.py",
            "#!/usr/bin/env python3\n"
            "from pathlib import Path\n"
            f"Path({str(cls.fake_root_marker)!r}).write_text('fake-root\\n')\n",
        )
        cls.target_root_makefile = cls.fixture_root / "target-root.mk"
        cls.target_root_makefile.write_text(
            "check: override ROOT := " + str(cls.fake_root) + "\n", encoding="utf-8"
        )
        cls.replacement_makefile = cls.fixture_root / "replacement.mk"
        cls.replacement_makefile.write_text(
            "check:\n\t@/usr/bin/touch "
            + cls.shell_quote(cls.replacement_marker)
            + "\n",
            encoding="utf-8",
        )
        cls.append_makefile = cls.fixture_root / "append.mk"
        cls.append_makefile.write_text(
            "build check lint root-test test verify __repository-make-authority: MAKEFILE_LIST := "
            + str(cls.repository_link / "Makefile")
            + "\n"
            "check::\n\t@/usr/bin/touch "
            + cls.shell_quote(cls.append_marker)
            + "\n",
            encoding="utf-8",
        )
        cls.startup_makefile = cls.fixture_root / "startup.mk"
        cls.startup_makefile.write_text(
            "$(shell /usr/bin/touch "
            + cls.shell_quote(cls.startup_marker)
            + ")\n",
            encoding="utf-8",
        )

    @classmethod
    def tearDownClass(cls):
        cls.temporary_directory.cleanup()

    @staticmethod
    def shell_quote(path):
        return "'" + str(path).replace("'", "'\\''") + "'"

    @staticmethod
    def write_executable(path, content):
        path.write_text(content, encoding="utf-8")
        path.chmod(0o755)

    def setUp(self):
        for marker in (
            self.baseline_marker,
            self.native_marker,
            self.root_test_marker,
            self.fake_shell_marker,
            self.fake_python_marker,
            self.fake_xcode_marker,
            self.fake_root_marker,
            self.replacement_marker,
            self.append_marker,
            self.startup_marker,
            self.hostile_marker,
        ):
            marker.unlink(missing_ok=True)

    def trusted_environment(self):
        environment = os.environ.copy()
        environment["PATH"] = str(self.fake_bin) + os.pathsep + environment["PATH"]
        environment.pop("MAKEFILES", None)
        return environment

    def run_make(self, *arguments, cwd=None, environment=None, expected=0, makefile=None):
        command = [
            str(SYSTEM_MAKE),
            "--no-print-directory",
            "-f",
            str(makefile or self.repository / "Makefile"),
            *arguments,
        ]
        result = subprocess.run(
            command,
            cwd=cwd or self.repository,
            env=environment or self.trusted_environment(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
            check=False,
        )
        if expected is None:
            return result
        self.assertEqual(result.returncode, expected, result.stdout)
        return result

    def test_repository_aliases_run_owned_tools_from_any_directory(self):
        for target in ("check", "lint", "build", "root-test", "test", "verify"):
            for cwd in (self.repository, self.external_directory):
                with self.subTest(target=target, cwd=cwd.name):
                    self.setUp()
                    self.run_make(
                        target,
                        "SHELL=" + str(self.fake_shell),
                        "PYTHON=" + str(self.fake_bin / "python3"),
                        "XCODEBUILD=" + str(self.fake_bin / "xcodebuild"),
                        cwd=cwd,
                    )
                    self.assertFalse(self.fake_shell_marker.exists())
                    self.assertFalse(self.fake_python_marker.exists())
                    self.assertFalse(self.fake_xcode_marker.exists())
                    if target in ("check", "lint", "build", "test", "verify"):
                        self.assertTrue(self.baseline_marker.exists())
                    if target in ("root-test", "verify"):
                        self.assertTrue(self.root_test_marker.exists())
                    if target in ("test", "verify"):
                        self.assertTrue(self.native_marker.exists())

    def test_startup_and_later_makefiles_fail_closed_at_the_documented_boundary(self):
        environment = self.trusted_environment()
        environment["MAKEFILES"] = str(self.startup_makefile)
        result = self.run_make("check", environment=environment, expected=None)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertTrue(self.startup_marker.exists())
        self.assertFalse(self.baseline_marker.exists())

        self.setUp()
        result = self.run_make(
            "-f", str(self.target_root_makefile), "check", expected=None
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertFalse(self.fake_root_marker.exists())
        self.assertFalse(self.baseline_marker.exists())

        self.setUp()
        result = self.run_make(
            "-f", str(self.replacement_makefile), "check", expected=None
        )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertFalse(self.replacement_marker.exists())
        self.assertFalse(self.baseline_marker.exists())

    def test_later_double_colon_recipe_is_explicit_caller_authority(self):
        self.run_make(
            "-f",
            str(self.append_makefile),
            "check",
            makefile=self.repository_link / "Makefile",
        )
        self.assertTrue(self.baseline_marker.exists())
        self.assertTrue(self.append_marker.exists())

    def test_nonexecuting_and_error_ignoring_modes_are_rejected(self):
        for flag in (
            "-n",
            "--just-print",
            "--dry-run",
            "--recon",
            "-t",
            "--touch",
            "-q",
            "--question",
            "-i",
            "--ignore-errors",
        ):
            with self.subTest(flag=flag):
                result = self.run_make(flag, "check", expected=None)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("non-executing or error-ignoring", result.stdout)
                self.assertFalse(self.baseline_marker.exists())

        result = self.run_make("MAKEFLAGS=-n", "check", expected=None)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("MAKEFLAGS must not be overridden", result.stdout)

    def test_hostile_shell_path_is_quoted_but_make_syntax_is_preload_authority(self):
        shell_hostile_repository = self.fixture_root / "hostile '; `touch nope`; spaces"
        shutil.copytree(self.repository, shell_hostile_repository)
        result = self.run_make(
            "check", makefile=shell_hostile_repository / "Makefile", expected=None
        )
        self.assertEqual(result.returncode, 0, result.stdout)

        hostile_repository = self.fixture_root / (
            "hostile $(shell touch " + str(self.hostile_marker) + ") ' checkout"
        )
        shutil.copytree(self.repository, hostile_repository)
        result = self.run_make(
            "check", makefile=hostile_repository / "Makefile", expected=None
        )
        self.assertTrue(self.hostile_marker.exists())
        self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_documentation_states_enforced_and_unavoidable_boundaries(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        plan = (ROOT / "docs/plans/2026-06-21-make-trust-boundary.md").read_text(
            encoding="utf-8"
        )
        combined = "\n".join((readme, agents, security, plan))
        for phrase in (
            "fixes `/bin/sh`",
            "non-executing or error-ignoring modes",
            "startup Makefiles can execute parse-time code before rejection",
            "later double-colon recipes remain caller authority",
            "Make syntax in an explicit `-f` path is evaluated before the repository loads",
            "`/usr/bin/make`",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, combined)


if __name__ == "__main__":
    unittest.main(verbosity=2)
