"""The printer and material a build is for, from printers.toml: the printer's plate, and the fits the
calibration piece showed for that material on it.

`--printer <name>` and `--material <name>` on the command line pick them; without them, the file's
defaults. Every part reads them from here (README.md, Calibration).
"""

import re
import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace

# Clearance a side, in mm, of the calibration piece's columns, from tight to loose.
GRIPS = (0, 0.05, 0.1, 0.15, 0.2)
SLIDES = (0.1, 0.15, 0.2, 0.25, 0.3)
# Every letter a row of the calibration piece has been engraved with: the fit it measures, and the clearance of each
# of its columns. A feature on the piece is engraved with its row's letter and its column's number, such as N2, and
# printers.toml holds that code, so a code keeps its meaning for good. A row that needs looser fits gets columns
# added at the end of its own tuple; one that needs tighter fits gets a new letter here, and ROWS moves to it. A
# letter is never taken out and a column never shifted, so the codes printers.toml already holds still read.
CODES = {
    "S": ("screw_hole", SLIDES),
    "N": ("nut_pocket", GRIPS),
    "P": ("printed_grip", GRIPS),
}
# The letter each fit's row on the piece is engraved with now.
ROWS = {"screw_hole": "S", "nut_pocket": "N", "printed_grip": "P"}
# Each fit, with its row's letter and columns as the piece is printed now.
FITS = {fit: (letter, CODES[letter][1]) for fit, letter in ROWS.items()}


def clearance(fit, code, where, codes=CODES):
    """The clearance a side a code read off the calibration piece stands for, such as N2 for nut_pocket: from
    whichever letter the fit's row had when the piece was printed."""
    m = re.fullmatch(r"([A-Z])([1-9][0-9]*)", code) if isinstance(code, str) else None
    letter, column = (m.group(1), int(m.group(2))) if m else (None, 0)
    if letter not in codes or codes[letter][0] != fit or column > len(codes[letter][1]):
        ranges = ", ".join(f"{k}1 to {k}{len(c)}" for k, (f, c) in codes.items() if f == fit)
        sys.exit(f"printers.py: {where} {fit} is {code!r}; it takes a code from its row on the calibration piece: {ranges}")
    return codes[letter][1][column - 1]


PRINTERS = Path(__file__).resolve().parent.parent / "printers.toml"


def _arg(argv, flag, default):
    if flag not in argv:
        return default
    i = argv.index(flag)
    if i + 1 >= len(argv):
        sys.exit(f"printers.py: {flag} takes a name from printers.toml")
    return argv[i + 1]


def printing(argv=None, path=PRINTERS):
    """The printer and material argv asks for, the command line's by default, or the file's defaults, without their
    fits, which a material not yet calibrated does not have: name, material, model, plate and nozzle."""
    argv = sys.argv if argv is None else argv
    data = tomllib.loads(path.read_text())
    name = _arg(argv, "--printer", data["default_printer"])
    material = _arg(argv, "--material", data["default_material"])
    if name not in data["printers"]:
        sys.exit(f"printers.py: no printer {name} in printers.toml: {', '.join(data['printers'])}")
    p = data["printers"][name]
    materials = p.get("materials", {})
    if material not in materials:
        sys.exit(f"printers.py: printer {name} has no {material} in printers.toml: give it a table "
                 f"and print the calibration piece in it (README.md, Calibration); it has "
                 f"{', '.join(materials) or 'none'}")
    m = materials[material]
    return SimpleNamespace(
        name=name, material=material, model=p["model"], plate=p["plate"], nozzle=p["nozzle"],
        table=m, default=(name, material) == (data["default_printer"], data["default_material"]))


def chosen(argv=None, path=PRINTERS):
    """printing(), with whether the material is calibrated and its fits, which a build of a part needs."""
    c = printing(argv, path)
    m = c.table
    missing = [f for f in ("calibrated", *FITS) if f not in m]
    if missing:
        sys.exit(f"printers.py: {c.name} in {c.material} has no {', '.join(missing)} in printers.toml: print the "
                 f"calibration piece in it (README.md, Calibration)")
    c.calibrated = m["calibrated"]
    c.fits = SimpleNamespace(**{f: clearance(f, m[f], f"{c.name} in {c.material}") for f in FITS})
    return c
