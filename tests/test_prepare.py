import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import prepare_source


class PrepareTests(unittest.TestCase):
    def test_unique_anchor(self):
        self.assertEqual(prepare_source.replace_once("a\nb", "a", "c"), "c\nb")

    def test_missing_anchor(self):
        with self.assertRaises(ValueError):
            prepare_source.replace_once("abc", "x", "c")

    def test_duplicate_anchor(self):
        with self.assertRaises(ValueError):
            prepare_source.replace_once("aa", "a", "b")

    def test_board_manifest(self):
        import json
        config = json.loads((ROOT / "board" / "config.json").read_text())
        self.assertEqual(config["type"], "xiao-family-robot")
        self.assertEqual(config["target"], "esp32s3")
        self.assertIn("CONFIG_WAKE_WORD_DISABLED=y", config["builds"][0]["sdkconfig_append"])

    def test_prepare_reuses_recorded_dependency_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "firmware-built").mkdir()
            lock = "test fixture dependency resolution"
            (root / "firmware-built" / "dependencies.lock").write_text(lock)
            archive = root / "source.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr(
                    f"xiaozhi-esp32-{prepare_source.REVISION}/README.md", "test fixture"
                )
            destination = root / "work" / "xiaozhi"
            with patch.object(prepare_source, "ROOT", root), patch.object(
                prepare_source, "patch"
            ):
                prepare_source.prepare(archive, destination)
            self.assertEqual((destination / "dependencies.lock").read_text(), lock)


if __name__ == "__main__":
    unittest.main()
