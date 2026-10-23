import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/core/subscription_self_check.py"
spec = importlib.util.spec_from_file_location("subscription_self_check", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SafeError(Exception):
    pass


class PublicContractTest(unittest.TestCase):
    def test_other_profile_is_not_intercepted(self):
        self.assertIsNone(module.evaluate({"kind": "openai"}, lambda _profile: None))

    def test_ready_is_local_and_reports_zero_calls(self):
        seen = []
        result = module.evaluate({"kind": module.KIND}, lambda profile: seen.append(profile))
        self.assertTrue(result["ok"])
        self.assertEqual((result["network_calls"], result["model_calls"]), (0, 0))
        self.assertEqual(len(seen), 1)

    def test_allowlisted_policy_message_is_preserved(self):
        def reject(_profile):
            raise SafeError("select account and model")
        result = module.evaluate({"kind": module.KIND}, reject, (SafeError,))
        self.assertFalse(result["ok"])
        self.assertEqual(result["message"], "select account and model")

    def test_unknown_exception_is_redacted(self):
        def fail(_profile):
            raise RuntimeError("secret-profile-value")
        result = module.evaluate({"kind": module.KIND}, fail, (SafeError,))
        self.assertFalse(result["ok"])
        self.assertNotIn("secret-profile-value", repr(result))

    def test_source_has_no_transport_or_process_calls(self):
        text = SOURCE.read_text(encoding="utf-8").lower()
        for forbidden in ("httpx", "requests", "socket", "subprocess", "openai", "websocket"):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
