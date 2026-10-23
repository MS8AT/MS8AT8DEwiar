"""Автономный контракт PATCH-012: без сети, аккаунтов и моделей."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "core" / "subscription_model_probe_guard.py"
sys.path.insert(0, str(SOURCE.parent))

import subscription_model_probe_guard as guard  # noqa: E402


class PublicContractTests(unittest.TestCase):
    def test_subscription_profiles_never_use_generic_probe(self):
        for transport in ("codex", "siwc", None):
            self.assertFalse(guard.should_probe({"kind": guard.SUBSCRIPTION_KIND,
                                                 "subscription_transport": transport, "model": "m"}))

    def test_ordinary_profiles_keep_generic_probe(self):
        self.assertTrue(guard.should_probe({"kind": "openai", "base_url": "local", "model": "m"}))
        self.assertTrue(guard.should_probe({"base_url": "local", "model": "m"}))

    def test_invalid_input_fails_closed(self):
        for value in (None, {}, "profile", [], 0):
            self.assertFalse(guard.should_probe(value))

    def test_source_has_no_side_effect_adapters(self):
        text = SOURCE.read_text(encoding="utf-8").lower()
        for forbidden in ("httpx", "requests", "socket", "subprocess", "openai", "websocket", "threading"):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
