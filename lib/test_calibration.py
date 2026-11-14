"""calibration.py: the piece it builds and the files it writes.

Run with `bin/part --test`.
"""

import tempfile
import unittest
import zipfile
from pathlib import Path

import calibration
from printers import FITS


class Piece(unittest.TestCase):
    def test_the_piece_is_one_valid_solid(self):
        s = calibration.piece()
        self.assertTrue(s.is_valid)
        self.assertEqual(len(s.solids()), 1)

    def test_it_has_a_row_for_every_fit(self):
        self.assertEqual(set(calibration.CUTS), set(FITS))
        self.assertEqual(set(calibration.SIZES), set(FITS))

    def test_every_feature_is_cut(self):
        for fit, (_, columns) in FITS.items():
            for c in (columns[0], columns[-1]):
                self.assertGreater(calibration.CUTS[fit](c).volume, 0, f"{fit} at {c}")

    def test_a_looser_column_cuts_more(self):
        for fit, (_, columns) in FITS.items():
            self.assertLess(calibration.CUTS[fit](columns[0]).volume, calibration.CUTS[fit](columns[-1]).volume, fit)

    def test_the_peg_is_its_size(self):
        size = calibration.peg().bounding_box().size
        self.assertAlmostEqual(size.X, calibration.PEG)
        self.assertAlmostEqual(size.Z, calibration.PEG_LENGTH)


class Export(unittest.TestCase):
    def test_a_plate_too_small_for_the_piece_stops(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(SystemExit, "more than the 50 mm plate"):
                calibration.export(Path(d), 50)
            self.assertFalse((Path(d) / "calibration.3mf").exists())

    def test_it_writes_the_piece_and_its_peg_as_a_bambu_studio_project(self):
        with tempfile.TemporaryDirectory() as d:
            size = calibration.export(Path(d), 256)
            with zipfile.ZipFile(Path(d) / "calibration.3mf") as z:
                names = z.read("Metadata/model_settings.config").decode()
            self.assertIn('value="calibration"', names)
            self.assertIn('value="peg"', names)
            self.assertGreater((Path(d) / "calibration.stl").stat().st_size, 0)
            self.assertAlmostEqual(size.Z, calibration.THICKNESS, places=5)


if __name__ == "__main__":
    unittest.main()
