import ast
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
tree = ast.parse((ROOT / "make_illustrated_guide.py").read_text(encoding="utf-8"))
values = {
    node.targets[0].id: node.value
    for node in tree.body
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
}
NETS = ast.literal_eval(values["NETS"])
WIRES = ast.literal_eval(values["WIRES"])


class IllustrationTests(unittest.TestCase):
    def test_supply_rows_are_separate(self):
        self.assertEqual(NETS[10][0], "GND")
        self.assertEqual(NETS[11][0], "3V3")
        self.assertEqual(NETS[15][0], "5V")
        self.assertNotIn(14, NETS)
        self.assertNotIn(19, NETS)

    def test_wires_match_actual_firmware_gpio(self):
        config = (ROOT / "board" / "config.h").read_text()
        expected = {
            12: "kOledSda", 13: "kOledScl", 16: "kSpeakerBclk",
            17: "kSpeakerLrck", 18: "kSpeakerData", 20: "kHeadButton",
            21: "kPanSignal", 22: "kTiltSignal",
        }
        for row, name in expected.items():
            gpio = int(re.search(r"GPIO(\d+)", NETS[row][0]).group(1))
            self.assertRegex(config, rf"{name}\s*=\s*GPIO_NUM_{gpio};")

    def test_no_two_destinations_use_the_same_hole(self):
        destinations = [(column, row) for _, _, row, column, *_ in WIRES]
        self.assertEqual(len(destinations), len(set(destinations)))
        self.assertTrue(all(column in "bcde" and row in NETS for column, row in destinations))
        self.assertNotIn(("a", 10), destinations)

    def test_ground_source_is_explicitly_reused(self):
        ground = [item for item in WIRES if item[2] == 10]
        self.assertEqual(len(ground), 2)
        self.assertFalse(ground[0][-1])
        self.assertTrue(ground[1][-1])
        self.assertEqual([item[3] for item in ground], ["b", "c"])

    def test_display_and_audio_have_all_required_signals(self):
        self.assertEqual({wire[5] for wire in WIRES if wire[4] == "OLED"},
                         {"GND", "VCC", "SDA", "SCL"})
        self.assertEqual({wire[5] for wire in WIRES if wire[4] == "MAX98357"},
                         {"GND", "VIN", "BCLK", "LRC / LRCK", "DIN"})

    def test_images_are_self_contained_valid_svg(self):
        paths = list((ROOT / "docs" / "images").glob("*.svg"))
        self.assertEqual(len(paths), 28)
        for path in paths:
            svg = ET.parse(path).getroot()
            self.assertEqual(svg.tag, "{http://www.w3.org/2000/svg}svg")
            self.assertIn("viewBox", svg.attrib)
            self.assertNotIn("width", svg.attrib)
            self.assertNotIn("height", svg.attrib)
            self.assertNotIn("<image", path.read_text(encoding="utf-8"))

    def test_completed_diagrams_match_all_wires(self):
        for name, module, expected in [("complete-oled", "OLED", 8), ("complete-core", None, 17)]:
            root = ET.parse(ROOT / "docs" / "images" / f"{name}.svg").getroot()
            ports = {(float(circle.attrib["cx"]), float(circle.attrib["cy"]))
                     for circle in root.findall(".//{http://www.w3.org/2000/svg}circle")
                     if circle.attrib.get("r") == "6"}
            wires = [wire for wire in WIRES if module is None or wire[4] == module]
            holes = {("a", wire[2]) for wire in wires} | {(wire[3], wire[2]) for wire in wires}
            positions = set()
            for col, row in holes:
                i = "abcdefghij".index(col)
                positions.add((222 + i * 19 + (25 if i >= 5 else 0), 83 + (row - 10) * 23))
            self.assertEqual(ports, positions)
            self.assertEqual(len(ports), expected)

    def test_flashing_dependency_matches_manual(self):
        requirement = (ROOT / "requirements-flash.txt").read_text().strip()
        self.assertEqual(requirement, "esptool==5.6.0")
        generator = (ROOT / "make_illustrated_guide.py").read_text()
        self.assertIn("pip install -r requirements-flash.txt", generator)
        self.assertIn("pymanager install 3.12", generator)

    def test_login_capture_exists_and_is_png(self):
        capture = ROOT / "docs" / "images" / "xiaozhi-login-20261028.png"
        self.assertTrue(capture.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))


if __name__ == "__main__":
    unittest.main()
