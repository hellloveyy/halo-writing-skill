import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "halo-writing/scripts/keychain_headers.py"
spec = importlib.util.spec_from_file_location("keychain_headers", SCRIPT)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class KeychainHeadersTests(unittest.TestCase):
    def result(self, value=b"", code=0):
        return subprocess.CompletedProcess([], code, stdout=value, stderr=b"PRIVATE_DIAGNOSTIC")

    def assert_rejected(self, result):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(helper.subprocess, "run", return_value=result), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = helper.main()
        self.assertEqual(code, 1)
        self.assertEqual(out.getvalue(), "")
        self.assertTrue(err.getvalue().strip())
        self.assertNotIn("PRIVATE_DIAGNOSTIC", err.getvalue())

    def test_valid_password_becomes_bearer_header(self):
        with patch.object(helper.subprocess, "run", return_value=self.result(b"test-only-password\n")):
            self.assertEqual(helper.load_headers(), {"Authorization": "Bearer test-only-password"})

    def test_custom_service_and_account_select_the_correct_record(self):
        def keychain(args, **kwargs):
            matches = args[args.index("-s") + 1] == "test.service" and args[args.index("-a") + 1] == "test.account"
            return self.result(b"test-only-password\n", 0 if matches else 44)
        with patch.object(helper.subprocess, "run", side_effect=keychain):
            try:
                result = helper.load_headers(service="test.service", account="test.account")
            except TypeError:
                self.fail("Selecting a per-site Keychain record is not implemented")
        self.assertEqual(result, {"Authorization": "Bearer test-only-password"})

    def test_keychain_error_never_prints_password_or_raw_diagnostics(self):
        self.assert_rejected(self.result(b"test-only-password", 44))

    def test_empty_password_is_rejected(self):
        self.assert_rejected(self.result(b"\n"))

    def test_header_injection_is_rejected(self):
        self.assert_rejected(self.result(b"test-only-password\r\nX-Injected: yes\n"))

    def test_non_ascii_password_is_rejected(self):
        self.assert_rejected(self.result(b"\xff"))

    def test_timeout_has_no_sensitive_output(self):
        out, err = io.StringIO(), io.StringIO()
        error = subprocess.TimeoutExpired("security", 15, output=b"PRIVATE_DIAGNOSTIC")
        with patch.object(helper.subprocess, "run", side_effect=error), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = helper.main()
        self.assertEqual(code, 1)
        self.assertEqual(out.getvalue(), "")
        self.assertNotIn("PRIVATE_DIAGNOSTIC", err.getvalue())


if __name__ == "__main__":
    unittest.main()
