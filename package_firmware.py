import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "work" / "xiaozhi"
BUILD = SOURCE / "build"
DEST = ROOT / "firmware-built"


def main():
    if not (BUILD / "merged-binary.bin").is_file():
        raise FileNotFoundError("No built firmware; compile first")
    configuration = (SOURCE / "sdkconfig").read_text(encoding="utf-8")
    required = [
        "CONFIG_BOARD_TYPE_XIAO_FAMILY_ROBOT=y",
        "CONFIG_ESPTOOLPY_FLASHSIZE_8MB=y",
        "CONFIG_LANGUAGE_EN_US=y",
        "CONFIG_WAKE_WORD_DISABLED=y",
    ]
    for item in required:
        if item not in configuration.splitlines():
            raise ValueError(f"Refusing package: missing {item}")
    stamp = json.loads((SOURCE / ".family-robot.json").read_text(encoding="utf-8"))
    DEST.mkdir(exist_ok=True)
    shutil.copy2(BUILD / "merged-binary.bin", DEST / "robot.bin")
    shutil.copy2(SOURCE / "sdkconfig", DEST / "sdkconfig.txt")
    if (SOURCE / "dependencies.lock").exists():
        shutil.copy2(SOURCE / "dependencies.lock", DEST / "dependencies.lock")
    stamp["sha256"] = hashlib.sha256((DEST / "robot.bin").read_bytes()).hexdigest()
    stamp["idf"] = "v6.0.1"
    (DEST / "manifest.json").write_text(json.dumps(stamp, indent=2), encoding="utf-8")
    print(f"Built firmware and hash saved in {DEST}")


if __name__ == "__main__":
    main()
