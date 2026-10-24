import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import urllib.request
import zipfile

REVISION = "f443114fe7c3fa26b10d3630090119891cd1c4fd"
ROOT = Path(__file__).resolve().parent
DESTINATION = ROOT / "work" / "xiaozhi"
HASHES = {
    "main/CMakeLists.txt": "e271f0ded771a371f78472ad66c7518dad5d1c162d43eaedb2f3e6cf41299b70",
    "main/Kconfig.projbuild": "ec95be32bbc57665e818c23c976f6892821736c53c7242ca6ccdc45799923722",
    "main/ota.cc": "d88e45c9678085e8e23c113f0fced2c43e64c4a3d927f507a1f8204319549eca",
}
BOARD = "xiao-family-robot"


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Expected exactly one upstream patch anchor: {old[:65]!r}")
    return text.replace(old, new, 1)


def patch(source):
    for name, expected in HASHES.items():
        actual = hashlib.sha256((source / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Unexpected upstream contents for {name}: {actual}")
    cmake_path = source / "main" / "CMakeLists.txt"
    cmake = cmake_path.read_text(encoding="utf-8")
    cmake = replace_once(cmake, "if(CONFIG_BOARD_TYPE_BREAD_COMPACT_WIFI)\n",
        'if(CONFIG_BOARD_TYPE_XIAO_FAMILY_ROBOT)\n'
        '    set(BOARD_DIR "xiao-family-robot")\n'
        '    set(BUILTIN_TEXT_FONT font_noto_sans_basic_14_1)\n'
        '    set(BUILTIN_ICON_FONT font_material_symbols_14_1)\n'
        'elseif(CONFIG_BOARD_TYPE_BREAD_COMPACT_WIFI)\n')
    cmake_path.write_text(cmake, encoding="utf-8", newline="\n")

    kconfig_path = source / "main" / "Kconfig.projbuild"
    kconfig = kconfig_path.read_text(encoding="utf-8")
    kconfig = replace_once(kconfig,
        '    config BOARD_TYPE_ATK_DNESP32S3\n',
        '    config BOARD_TYPE_XIAO_FAMILY_ROBOT\n'
        '        bool "XIAO Family Robot (SH1106, PDM, camera, head)"\n'
        '        depends on IDF_TARGET_ESP32S3\n\n'
        '    config BOARD_TYPE_ATK_DNESP32S3\n')
    kconfig_path.write_text(kconfig, encoding="utf-8", newline="\n")

    ota_path = source / "main" / "ota.cc"
    ota = ota_path.read_text(encoding="utf-8")
    anchor = ("bool Ota::Upgrade(const std::string& firmware_url, "
              "std::function<void(int progress, size_t speed)> callback) {\n")
    ota = replace_once(ota, anchor, anchor +
        '#if CONFIG_BOARD_TYPE_XIAO_FAMILY_ROBOT\n'
        '    ESP_LOGE(TAG, "Family Robot: network firmware upgrades disabled; rebuild and flash by USB.");\n'
        '    return false;\n'
        '#endif\n')
    ota_path.write_text(ota, encoding="utf-8", newline="\n")

    target = source / "main" / "boards" / BOARD
    shutil.copytree(ROOT / "board", target)
    stamp = {"revision": REVISION, "board": BOARD}
    (source / ".family-robot.json").write_text(json.dumps(stamp, indent=2), encoding="utf-8")


def prepare(archive, destination=DESTINATION):
    if destination.exists():
        raise FileExistsError(
            f"{destination} already exists. No files were overwritten. "
            "To rebuild, use build.ps1. For a new clean preparation, extract the package "
            "to another empty short folder.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix="prepare-") as temp:
        staging = Path(temp)
        source = staging / "source"
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.infolist():
                parts = PurePosixPath(member.filename).parts
                if not parts or parts[0] != f"xiaozhi-esp32-{REVISION}":
                    raise ValueError("Unexpected archive root")
                target = source.joinpath(*parts[1:])
                if not target.resolve().is_relative_to(source.resolve()):
                    raise ValueError("Archive contains an unsafe path")
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with bundle.open(member) as inp, target.open("wb") as out:
                        shutil.copyfileobj(inp, out)
        patch(source)
        lockfile = ROOT / "firmware-built" / "dependencies.lock"
        if lockfile.is_file():
            shutil.copy2(lockfile, source / "dependencies.lock")
        shutil.move(str(source), destination)
    print(f"Prepared pinned source: {destination}")
    print("Next: run build.ps1 in the ESP-IDF 6.0.1 PowerShell terminal.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, help="Use an existing official revision ZIP")
    args = parser.parse_args()
    if args.archive:
        prepare(args.archive)
    else:
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "upstream.zip"
            url = f"https://codeload.github.com/78/xiaozhi-esp32/zip/{REVISION}"
            print(f"Downloading public source: {url}", flush=True)
            with urllib.request.urlopen(url, timeout=120) as response, archive.open("wb") as out:
                shutil.copyfileobj(response, out)
            prepare(archive)


if __name__ == "__main__":
    main()
