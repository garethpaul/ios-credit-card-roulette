#!/usr/bin/env python3
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class MakeTrustBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary_directory = tempfile.TemporaryDirectory(
            prefix="card-roulette-make-boundary-"
        )
        cls.fixture_root = Path(cls.temporary_directory.name)
        cls.repository = cls.fixture_root / "repository"
        cls.external_directory = cls.fixture_root / "external working directory"
        cls.fake_root = cls.fixture_root / "fake-root"
        cls.fake_bin = cls.fixture_root / "fake-bin"
        cls.repository_scripts = cls.repository / "scripts"
        cls.fake_root_scripts = cls.fake_root / "scripts"

        cls.repository_scripts.mkdir(parents=True)
        cls.external_directory.mkdir()
        cls.fake_root_scripts.mkdir(parents=True)
        cls.fake_bin.mkdir()
        shutil.copy2(ROOT / "Makefile", cls.repository / "Makefile")

        cls.baseline_marker = cls.fixture_root / "baseline.marker"
        cls.native_marker = cls.fixture_root / "native.marker"
        cls.fake_shell_marker = cls.fixture_root / "fake-shell.marker"
        cls.fake_python_marker = cls.fixture_root / "fake-python.marker"
        cls.fake_root_marker = cls.fixture_root / "fake-root.marker"
        cls.replacement_marker = cls.fixture_root / "replacement.marker"
        cls.startup_marker = cls.fixture_root / "startup.marker"

        cls.write_executable(
            cls.repository_scripts / "check-baseline.py",
            "#!/usr/bin/env python3\n"
            "from pathlib import Path\n"
            f"Path({str(cls.baseline_marker)!r}).write_text('baseline\\n')\n",
        )
        cls.write_executable(
            cls.repository_scripts / "run-tests.sh",
            "#!/bin/sh\n"
            "set -eu\n"
            f"printf '%s\\n' native > {cls.shell_quote(cls.native_marker)}\n",
        )
        cls.write_executable(cls.fake_bin / "python3", cls.python_launcher())
        cls.write_executable(cls.fake_bin / "xcodebuild", "#!/bin/sh\nexit 0\n")

        cls.fake_shell = cls.fixture_root / "fake-shell"
        cls.write_executable(
            cls.fake_shell,
            "#!/bin/sh\n"
            f"printf '%s\\n' fake-shell > {cls.shell_quote(cls.fake_shell_marker)}\n"
            "exit 0\n",
        )
        cls.fake_python_bin = cls.fixture_root / "fake-python-bin"
        cls.fake_python_bin.mkdir()
        cls.write_executable(
            cls.fake_python_bin / "python3",
            "#!/bin/sh\n"
            f"printf '%s\\n' fake-python > {cls.shell_quote(cls.fake_python_marker)}\n"
            "exit 0\n",
        )
        cls.write_executable(cls.fake_python_bin / "xcodebuild", "#!/bin/sh\nexit 1\n")

        cls.write_executable(
            cls.fake_root_scripts / "check-baseline.py",
            "#!/usr/bin/env python3\n"
            "from pathlib import Path\n"
            f"Path({str(cls.fake_root_marker)!r}).write_text('fake-root\\n')\n",
        )
        cls.target_root_makefile = cls.fixture_root / "target-root.mk"
        cls.target_root_makefile.write_text(
            "check: override ROOT := " + str(cls.fake_root) + "\n",
            encoding="utf-8",
        )
        cls.replacement_makefile = cls.fixture_root / "replacement.mk"
        replacement_recipe = (
            "\t@printf '%s\\n' replacement >> "
            + cls.shell_quote(cls.replacement_marker)
            + "\n"
        )
        cls.replacement_makefile.write_text(
            "check:\n"
            + replacement_recipe
            + "lint:\n"
            + replacement_recipe
            + "test:\n"
            + replacement_recipe
            + "build:\n"
            + replacement_recipe,
            encoding="utf-8",
        )
        cls.startup_makefile = cls.fixture_root / "startup.mk"
        cls.startup_makefile.write_text(
            "$(shell printf '%s\\n' startup > "
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

    @classmethod
    def python_launcher(cls):
        return (
            "#!/bin/sh\n"
            "exec " + cls.shell_quote(Path(sys.executable)) + ' "$@"\n'
        )

    @staticmethod
    def write_executable(path, content):
        path.write_text(content, encoding="utf-8")
        path.chmod(0o755)

    def setUp(self):
        for marker in (
            self.baseline_marker,
            self.native_marker,
            self.fake_shell_marker,
            self.fake_python_marker,
            self.fake_root_marker,
            self.replacement_marker,
            self.startup_marker,
        ):
            marker.unlink(missing_ok=True)

    def run_make(self, *arguments, cwd=None, environment=None):
        command = ["make", "-f", str(self.repository / "Makefile"), *arguments]
        result = subprocess.run(
            command,
            cwd=cwd or self.repository,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        return result.stdout

    def trusted_environment(self):
        environment = os.environ.copy()
        environment["PATH"] = str(self.fake_bin) + os.pathsep + environment["PATH"]
        environment.pop("MAKEFILES", None)
        return environment

    def test_canonical_and_external_aliases_execute_repository_checks(self):
        environment = self.trusted_environment()
        for target in ("check", "lint", "build", "test"):
            with self.subTest(target=target, cwd="repository"):
                self.setUp()
                self.run_make(target, environment=environment)
                self.assertTrue(self.baseline_marker.exists())
                self.assertEqual(self.native_marker.exists(), target == "test")
            with self.subTest(target=target, cwd="external"):
                self.setUp()
                self.run_make(target, cwd=self.external_directory, environment=environment)
                self.assertTrue(self.baseline_marker.exists())
                self.assertEqual(self.native_marker.exists(), target == "test")

    def test_caller_controlled_shell_and_path_are_outside_boundary(self):
        self.run_make("SHELL=" + str(self.fake_shell), "check")
        self.assertTrue(self.fake_shell_marker.exists())
        self.assertFalse(self.baseline_marker.exists())

        environment = os.environ.copy()
        environment["PATH"] = str(self.fake_python_bin) + os.pathsep + environment["PATH"]
        self.run_make("check", environment=environment)
        self.assertTrue(self.fake_python_marker.exists())
        self.assertFalse(self.baseline_marker.exists())

    def test_caller_make_programs_are_outside_boundary(self):
        environment = self.trusted_environment()
        environment["MAKEFILES"] = str(self.startup_makefile)
        self.run_make("check", environment=environment)
        self.assertTrue(self.startup_marker.exists())
        self.assertTrue(self.baseline_marker.exists())

        self.setUp()
        self.run_make(
            "-f",
            str(self.target_root_makefile),
            "check",
            environment=self.trusted_environment(),
        )
        self.assertTrue(self.fake_root_marker.exists())
        self.assertFalse(self.baseline_marker.exists())

        for target in ("check", "lint", "test", "build"):
            with self.subTest(replacement_target=target):
                self.setUp()
                self.run_make(
                    "-f",
                    str(self.replacement_makefile),
                    target,
                    environment=self.trusted_environment(),
                )
                self.assertTrue(self.replacement_marker.exists())
                self.assertFalse(self.baseline_marker.exists())
                self.assertFalse(self.native_marker.exists())

    def test_no_execution_flags_are_outside_boundary(self):
        for flag in ("-n", "-t"):
            with self.subTest(flag=flag):
                self.run_make(flag, "check", environment=self.trusted_environment())
                self.assertFalse(self.baseline_marker.exists())

    def test_documentation_states_exact_make_trust_boundary(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
        required_phrases = (
            "checked-in Makefile trust boundary",
            "caller-supplied extra or startup Makefiles",
            "caller-selected `SHELL`, `.SHELLFLAGS`, or `PATH` tools",
            "target-specific overrides or replacement recipes",
            "no-execution flags such as `-n` or `-t`",
        )
        for phrase in required_phrases:
            with self.subTest(document="README.md", phrase=phrase):
                self.assertIn(phrase, readme)
        self.assertIn("checked-in Makefile trust boundary", agents)
        self.assertIn("checked-in Makefile trust boundary", security)

    def test_documentation_matches_the_macos_workflow(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("`make test` on `macos-15`", readme)
        self.assertNotIn("baseline on Ubuntu", readme)


if __name__ == "__main__":
    unittest.main(verbosity=2)
