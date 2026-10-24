import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import package_firmware


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / "source"
        self.build = self.source / "build"
        self.dest = Path(self.temp.name) / "output"
        self.build.mkdir(parents=True)
        self.settings = [
            "CONFIG_BOARD_TYPE_XIAO_FAMILY_ROBOT=y",
            "CONFIG_ESPTOOLPY_FLASHSIZE_8MB=y",
            "CONFIG_LANGUAGE_EN_US=y",
            "CONFIG_WAKE_WORD_DISABLED=y",
        ]
        (self.source / "sdkconfig").write_text("\n".join(self.settings))
        (self.source / ".family-robot.json").write_text(
            json.dumps({"board": "xiao-family-robot", "revision": "test-fixture"})
        )
        self.payload = b"unit-test fixture, not firmware"
        (self.build / "merged-binary.bin").write_bytes(self.payload)
        self.paths = patch.multiple(
            package_firmware, SOURCE=self.source, BUILD=self.build, DEST=self.dest
        )
        self.paths.start()
        self.addCleanup(self.paths.stop)

    def test_package_copies_image_and_records_exact_hash(self):
        lock = "unit-test dependency resolution"
        (self.source / "dependencies.lock").write_text(lock)
        package_firmware.main()
        self.assertEqual((self.dest / "robot.bin").read_bytes(), self.payload)
        manifest = json.loads((self.dest / "manifest.json").read_text())
        self.assertEqual(manifest["board"], "xiao-family-robot")
        self.assertEqual(manifest["sha256"], hashlib.sha256(self.payload).hexdigest())
        self.assertEqual(manifest["idf"], "v6.0.1")
        self.assertEqual((self.dest / "dependencies.lock").read_text(), lock)

    def test_missing_image_is_rejected(self):
        (self.build / "merged-binary.bin").unlink()
        with self.assertRaises(FileNotFoundError):
            package_firmware.main()
        self.assertFalse(self.dest.exists())

    def test_each_required_configuration_is_enforced(self):
        for missing in self.settings:
            with self.subTest(missing=missing):
                (self.source / "sdkconfig").write_text(
                    "\n".join(setting for setting in self.settings if setting != missing)
                )
                with self.assertRaises(ValueError):
                    package_firmware.main()
                self.assertFalse(self.dest.exists())


if __name__ == "__main__":
    unittest.main()
