import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shlex
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "halo-writing/scripts/install_macos_helper.py"


class InstallHelperTests(unittest.TestCase):
    def setUp(self):
        if not SCRIPT.is_file():
            self.fail("The portable macOS helper installer is not implemented")
        spec = importlib.util.spec_from_file_location("install_macos_helper", SCRIPT)
        self.installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.installer)
        self.temp = tempfile.TemporaryDirectory(prefix="halo-writing-test-")
        self.addCleanup(self.temp.cleanup)
        self.destination = Path(self.temp.name) / "directory with spaces"

    def test_site_url_becomes_mcp_endpoint(self):
        self.assertEqual(self.installer.mcp_endpoint("https://blog.example.com/"), "https://blog.example.com/mcp")
        self.assertEqual(self.installer.mcp_endpoint("https://blog.example.com/mcp/"), "https://blog.example.com/mcp")

    def test_subpath_is_preserved(self):
        self.assertEqual(self.installer.mcp_endpoint("https://blog.example.com/blog"), "https://blog.example.com/blog/mcp")

    def test_rejects_insecure_or_credential_bearing_urls(self):
        for url in ("http://blog.example.com", "https://user:password@example.com", "https://blog.example.com?token=test", "https://blog.example.com/#fragment", "invalid"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.installer.mcp_endpoint(url)

    def test_installs_into_selected_directory_and_is_repeatable(self):
        first = self.installer.install_helper(self.destination)
        second = self.installer.install_helper(self.destination)
        self.assertEqual(first, second)
        self.assertEqual(first.read_bytes(), SCRIPT.with_name("keychain_headers.py").read_bytes())
        self.assertEqual(first.stat().st_mode & 0o777, 0o700)

    def test_does_not_replace_an_existing_different_file(self):
        self.destination.mkdir(parents=True)
        target = self.destination / "halo_writing_keychain_headers.py"
        target.write_text("existing customization")
        with self.assertRaises(FileExistsError):
            self.installer.install_helper(self.destination)
        self.assertEqual(target.read_text(), "existing customization")

    def test_generated_config_handles_spaces_and_per_site_credentials(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = self.installer.main(["--site", "https://blog.example.com", "--bin-dir", str(self.destination)], system="Darwin")
        self.assertEqual(code, 0)
        lines = output.getvalue().splitlines()
        setting = next(line for line in lines if line.startswith("http_headers_helper = "))
        command = json.loads(setting.split(" = ", 1)[1])
        arguments = shlex.split(command)
        self.assertEqual(Path(arguments[1]), self.destination.resolve() / "halo_writing_keychain_headers.py")
        self.assertIn("codex.halo.blog.example.com", arguments)
        self.assertIn('url = "https://blog.example.com/mcp"', lines)
        self.assertFalse((self.destination.parent / "config.toml").exists())

    def test_other_operating_systems_are_rejected(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = self.installer.main(["--site", "https://blog.example.com", "--bin-dir", str(self.destination)], system="Windows")
        self.assertEqual(code, 1)
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
