"""printers.py: choosing a printer and material, and reading the codes from the calibration piece.

Run with `bin/part --test`.
"""

import tempfile
import tomllib
import unittest
from pathlib import Path

from printers import CODES, FITS, PRINTERS, ROWS, chosen, clearance, printing

TOML = """
default_printer = "p2s"
default_material = "pla"

[printers.p2s]
model = "Bambu Lab P2S"
plate = 256
nozzle = 0.4

[printers.p2s.materials.pla]
calibrated = true
screw_hole = "S3"
nut_pocket = "N2"
printed_grip = "P1"

[printers.a1-mini]
model = "Bambu Lab A1 mini"
plate = 180
nozzle = 0.4

[printers.a1-mini.materials.petg]
calibrated = false
screw_hole = "S5"
nut_pocket = "N4"
printed_grip = "P5"
"""


class Chosen(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "printers.toml"
        self.path.write_text(TOML)

    def tearDown(self):
        self.dir.cleanup()

    def choose(self, *argv):
        return chosen(["part.py", *argv], self.path)

    def test_the_defaults_without_arguments(self):
        p = self.choose()
        self.assertEqual((p.name, p.material, p.plate, p.calibrated, p.default), ("p2s", "pla", 256, True, True))
        self.assertEqual((p.fits.screw_hole, p.fits.nut_pocket, p.fits.printed_grip), (0.2, 0.05, 0))

    def test_another_printer_and_material(self):
        p = self.choose("--printer", "a1-mini", "--material", "petg")
        self.assertEqual((p.name, p.material, p.plate, p.calibrated, p.default), ("a1-mini", "petg", 180, False, False))
        self.assertEqual((p.fits.screw_hole, p.fits.nut_pocket, p.fits.printed_grip), (0.3, 0.15, 0.2))

    def test_an_unknown_printer_stops(self):
        with self.assertRaisesRegex(SystemExit, "no printer x1"):
            self.choose("--printer", "x1")

    def test_a_material_not_calibrated_on_the_printer_stops(self):
        with self.assertRaisesRegex(SystemExit, "p2s has no petg.*it has pla"):
            self.choose("--material", "petg")

    def test_a_flag_without_its_name_stops(self):
        with self.assertRaisesRegex(SystemExit, "--printer takes a name"):
            self.choose("--printer")

    def test_a_material_without_fits_is_printed_but_not_built(self):
        self.path.write_text(TOML + '\n[printers.p2s.materials.petg]\ncalibrated = false\n')
        argv = ["calibration.py", "--material", "petg"]
        self.assertEqual(printing(argv, self.path).material, "petg")
        with self.assertRaisesRegex(SystemExit, "p2s in petg has no screw_hole.*calibration piece"):
            chosen(argv, self.path)

    def test_a_material_without_calibrated_stops(self):
        self.path.write_text(TOML.replace("calibrated = true\n", "", 1))
        with self.assertRaisesRegex(SystemExit, "has no calibrated"):
            self.choose()

    def test_a_missing_fit_stops(self):
        self.path.write_text(TOML.replace('printed_grip = "P1"\n', "", 1))
        with self.assertRaisesRegex(SystemExit, "p2s in pla has no printed_grip"):
            self.choose()


class Clearance(unittest.TestCase):
    def test_a_code_stands_for_its_column(self):
        for fit, (letter, columns) in FITS.items():
            for i, c in enumerate(columns):
                self.assertEqual(clearance(fit, f"{letter}{i + 1}", "here"), c)

    def test_a_code_from_another_row_stops(self):
        with self.assertRaisesRegex(SystemExit, "nut_pocket is 'S2'.*N1 to N5"):
            clearance("nut_pocket", "S2", "here")

    def test_a_column_past_the_row_stops(self):
        for code in ("N0", "N6", "N", "N22", "n2", "N02", 2):
            with self.assertRaises(SystemExit):
                clearance("nut_pocket", code, "here")

    def test_a_row_with_columns_added_reads_past_nine(self):
        codes = {"N": ("nut_pocket", tuple(i / 100 for i in range(12)))}
        self.assertEqual(clearance("nut_pocket", "N10", "here", codes), 0.09)
        self.assertEqual(clearance("nut_pocket", "N12", "here", codes), 0.11)
        with self.assertRaisesRegex(SystemExit, "N1 to N12"):
            clearance("nut_pocket", "N13", "here", codes)

    def test_an_older_letter_still_reads_after_a_row_moves_to_a_new_one(self):
        codes = {"N": ("nut_pocket", (0, 0.05)), "Q": ("nut_pocket", (-0.05, -0.02))}
        self.assertEqual(clearance("nut_pocket", "N2", "here", codes), 0.05)
        self.assertEqual(clearance("nut_pocket", "Q1", "here", codes), -0.05)
        with self.assertRaisesRegex(SystemExit, "N1 to N2, Q1 to Q2"):
            clearance("nut_pocket", "Q3", "here", codes)

    def test_every_row_is_a_letter_of_its_fit(self):
        for fit, letter in ROWS.items():
            self.assertEqual(CODES[letter][0], fit)


class TheFile(unittest.TestCase):
    def test_every_printer_and_material_in_printers_toml_reads(self):
        data = tomllib.loads(PRINTERS.read_text())
        for name, printer in data["printers"].items():
            for material, table in printer.get("materials", {}).items():
                argv = ["part.py", "--printer", name, "--material", material]
                printing(argv)
                if any(fit in table for fit in FITS):  # a material not calibrated yet has no fits, and builds no part
                    chosen(argv)


if __name__ == "__main__":
    unittest.main()
