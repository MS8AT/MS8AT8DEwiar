"""PATCH-010: отдельный блок проходит new, inspect, test и pack без сети."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "tools"))
import patch_block


class PatchBlockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "patches").mkdir()

    def test_full_lifecycle_is_local_and_reproducible(self):
        created = patch_block.new_block(self.root, "PATCH-123", "small_part")
        self.assertFalse(created["code_executed"])
        self.assertEqual(patch_block.inspect(self.root, "PATCH-123")["files"], 5)
        tested = patch_block.run_tests(self.root, "PATCH-123")
        self.assertTrue(tested["code_executed"])
        self.assertEqual(tested["tests"], ["verify.py", "tests/public_contract_test.py"])
        first = patch_block.pack(self.root, "PATCH-123")
        second = patch_block.pack(self.root, "PATCH-123", self.root / "again.zip")
        self.assertEqual(first["package_sha256"], second["package_sha256"])
        with zipfile.ZipFile(first["package"]) as archive:
            self.assertIn("PATCH-123/manifest.json", archive.namelist())

    def test_changed_or_extra_file_is_refused(self):
        patch_block.new_block(self.root, "PATCH-123", "small_part")
        source = self.root / "patches" / "PATCH-123" / "src" / "core" / "small_part.py"
        source.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            patch_block.inspect(self.root, "PATCH-123")
        patch_block.new_block(self.root, "PATCH-124", "other_part")
        (self.root / "patches" / "PATCH-124" / "extra.txt").write_text("extra", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "состав блока"):
            patch_block.inspect(self.root, "PATCH-124")

    def test_paths_and_existing_directory_fail_closed(self):
        for value in ("patch-123", "PATCH-12", "../PATCH-123", "PATCH-123/x"):
            with self.assertRaisesRegex(ValueError, "идентификатор"):
                patch_block.patch_dir(self.root, value)
        patch_block.new_block(self.root, "PATCH-123", "small_part")
        with self.assertRaisesRegex(ValueError, "уже существует"):
            patch_block.new_block(self.root, "PATCH-123", "small_part")

    def test_manifest_remains_small_and_human_readable(self):
        patch_block.new_block(self.root, "PATCH-123", "small_part")
        path = self.root / "patches" / "PATCH-123" / "manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema"], 1)
        self.assertEqual(data["id"], "PATCH-123")
        self.assertEqual(len(data["files"]), 5)


if __name__ == "__main__":
    unittest.main()
