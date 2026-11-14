"""The calibration piece: one flat plate that shows which fits a printer makes in a material.

Each row is one fit the parts depend on, made five times from tight to loose, and every feature has its code
engraved under it: its row's letter and its column's number, such as N2. Printed and tried with the real screw, nut
and peg, the code under the first feature in each row that fits goes into printers.toml for that printer and
material (README.md, Calibration). printers.py holds the letters and what each column's clearance is.

The piece is exported as a Bambu Studio project, as the parts are, and prints with the presets the parts print with
(printers.toml), so the fits read off it hold for them.

A loose peg prints beside the piece, for the row that tries a printed part in a printed hole. Built with
`bin/part --calibration`, with `--printer` and `--material` as for a part, into
build/calibration/<printer>-<material>/.
"""

import sys
from pathlib import Path

from build123d import Align, Box, Compound, Cylinder, Pos, RegularPolygon, Text, export_stl, extrude

# printers.py is beside this file; put its directory on the path, since Python's safe-path mode (-P or
# PYTHONSAFEPATH) leaves a script's own directory off it.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bambu  # noqa: E402
from printers import FITS, printing  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CUT = 1  # past a face, so a cut leaves no skin
MIN = (Align.MIN, Align.MIN, Align.MIN)

SCREW = 3.0  # an M3 screw's thread, ISO 4762
NUT_ACROSS_FLATS = 5.5  # an M3 hex nut, ISO 4032
NUT_THICKNESS = 2.4

THICKNESS = 4  # the plate: a nut's pocket and the floor under it
WEB = 3  # between two features side by side, and from a feature to the edge
NUT_FLOAT = 0.2  # a nut's pocket is this much deeper than the nut
PUSH_OUT = 3  # a hole under a pocket, to push the part back out
CODE_SIZE = 3.5  # the engraved codes' height
CODE_DEPTH = 0.6  # three layers
CODE_ROW = 5.5  # the strip under each row that holds its codes
PEG = 6  # the loose peg, across
PEG_LENGTH = 10


def through(d):
    return Pos(0, 0, -CUT) * Cylinder(d / 2, THICKNESS + 2 * CUT, align=(Align.CENTER, Align.CENTER, Align.MIN))


def pocket(shape, depth, from_below=False):
    """A pocket from the top face, or from the bottom one, which lies on the plate, with a hole through the rest to
    push the part back out."""
    z = -CUT if from_below else THICKNESS - depth
    return Pos(0, 0, z) * extrude(shape, depth + CUT) + through(PUSH_OUT)


# Each row, top to bottom: the cut a clearance a side makes, and the row's size across at its loosest. The nuts'
# pockets open on the face on the plate, the way a part prints a pocket a nut is pressed into from outside.
CUTS = {
    "screw_hole": lambda c: through(SCREW + 2 * c),
    "nut_pocket": lambda c: pocket(RegularPolygon((NUT_ACROSS_FLATS + 2 * c) / 2, 6, major_radius=False),
                                   NUT_THICKNESS + NUT_FLOAT, from_below=True),
    "printed_grip": lambda c: through(PEG + 2 * c),
}
SIZES = {
    "screw_hole": SCREW + 2 * max(FITS["screw_hole"][1]),
    "nut_pocket": (NUT_ACROSS_FLATS + 2 * max(FITS["nut_pocket"][1])) * 2 / 3 ** 0.5,
    "printed_grip": PEG + 2 * max(FITS["printed_grip"][1]),
}
COLUMNS = max(len(columns) for _, columns in FITS.values())
PITCH = max(max(SIZES.values()), 2.5 * CODE_SIZE) + WEB  # the columns line up down the rows, a code's width apart


def piece():
    width = COLUMNS * PITCH + WEB
    height = sum(WEB + SIZES[fit] + CODE_ROW for fit in FITS)
    s = Box(width, height, THICKNESS, align=MIN)
    y = height
    for fit, (letter, columns) in FITS.items():
        y -= WEB + SIZES[fit] / 2
        for i, c in enumerate(columns):
            x = WEB + PITCH * (i + 0.5)
            s -= Pos(x, y) * CUTS[fit](c)
            code = extrude(Text(f"{letter}{i + 1}", CODE_SIZE), CODE_DEPTH + CUT)
            s -= Pos(x, y - SIZES[fit] / 2 - CODE_ROW / 2, THICKNESS - CODE_DEPTH) * code
        y -= SIZES[fit] / 2 + CODE_ROW
    return s


def peg():
    """The loose peg, standing beside the piece, for the printed_grip row."""
    return Cylinder(PEG / 2, PEG_LENGTH, align=(Align.CENTER, Align.CENTER, Align.MIN))


def export(build, plate):
    """Write the piece and its peg into build: an STL, and a 3MF, a Bambu Studio project. Stops if they do not fit on
    a plate of that side. Gives the piece's size."""
    s = piece()
    if not s.is_valid or len(s.solids()) != 1:
        sys.exit("calibration.py: the piece is not one valid solid")
    size = s.bounding_box().size
    p = Pos(size.X + WEB + PEG, PEG) * peg()
    extent = p.bounding_box().max.X + PEG / 2
    if extent > plate or size.Y > plate:
        sys.exit(f"calibration.py: the piece and its peg take {extent:.0f} × {size.Y:.0f} mm, more than the {plate} mm plate")
    build.mkdir(parents=True, exist_ok=True)
    export_stl(Compound([s, p]), build / "calibration.stl")
    bambu.write_project(build / "calibration.3mf", [bambu.Part("calibration", s), bambu.Part("peg", p)])
    return size


def main():
    printer = printing()
    build = ROOT / "build" / "calibration" / f"{printer.name}-{printer.material}"  # not committed
    size = export(build, printer.plate)
    print(f"the calibration piece, {size.X:.0f} × {size.Y:.0f} × {THICKNESS:.0f} mm, top face up, and its peg standing beside it, "
          f"in {build.relative_to(ROOT)}/")
    print("the codes engraved under its features, and the clearance a side each stands for, in mm:")
    for fit, (letter, columns) in FITS.items():
        print(f"  {fit:<14}" + "".join(f"  {letter}{i + 1} {c:.2f}" for i, c in enumerate(columns)))


if __name__ == "__main__":
    main()
