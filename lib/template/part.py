"""NAME: what it is, where in the house it goes, and what it holds or fixes.

Every size is a named constant below. Coordinates: x across, y deep, z up from the face that lies on the plate.

Run through bin/part, which checks it and writes the printable files to build/.
"""

import sys
from pathlib import Path

from build123d import Align, Box, Cylinder, Pos

# What the parts share is in lib/; put it on the path, since bin/part's PYTHONPATH is not there when this file is
# run some other way.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import plate  # noqa: E402
from printers import chosen  # noqa: E402

HERE = Path(__file__).parent
# The fits the calibration piece showed for the printer and material the build is for (printers.toml).
FITS = chosen().fits
CUT = 1  # a cut runs this far past what it cuts through, so it leaves no skin
MIN = (Align.CENTER, Align.CENTER, Align.MIN)

WIDTH = 40
DEPTH = 20
THICKNESS = 4
SCREW = 3.0  # an M3 screw's thread, ISO 4762


def body():
    hole = Pos(0, 0, -CUT) * Cylinder(SCREW / 2 + FITS.screw_hole, THICKNESS + 2 * CUT, align=MIN)
    return Box(WIDTH, DEPTH, THICKNESS, align=MIN) - hole


def main():
    plate.run(HERE, printed={"body": body()})


if __name__ == "__main__":
    main()
