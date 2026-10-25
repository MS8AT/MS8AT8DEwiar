"""Пропуск, пустой вывод или ошибка не превращаются в успешную проверку."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_windows_candidate import classify


class ResultTest(unittest.TestCase):
    def test_failed_exit_wins(self):
        self.assertEqual(classify(1, "ALL OK"), "FAIL")

    def test_failed_assertion_wins(self):
        self.assertEqual(classify(0, "✅ сначала\n❌ затем"), "FAIL")

    def test_empty_is_not_success(self):
        self.assertEqual(classify(0, ""), "FAIL")

    def test_missing_dependency_is_skip(self):
        self.assertEqual(classify(0, "✅ пропуск: нет fastapi"), "SKIP")

    def test_partial_native_check(self):
        self.assertEqual(classify(0, "✅ контракт\nживую проверку пропускаю"), "PARTIAL_SKIP")

    def test_words_in_assertion_are_not_skip(self):
        self.assertEqual(classify(0, "✅ имя пропускается; skipped: False"), "PASS")

    def test_unittest_success(self):
        self.assertEqual(classify(0, "Ran 7 tests\n\nOK\n"), "PASS")


if __name__ == "__main__":
    unittest.main()
