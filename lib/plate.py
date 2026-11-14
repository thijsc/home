"""What every part's build does after its shapes are made: check them, set them out on the printer's plate, and
write the printable files, the STEP file and the pictures.

A part's part.py makes its shapes and hands them to run(). The printed shapes are given where they sit when the
thing is put together, so the check finds two that overlap; `turn` says how each lies on the plate.
"""

import sys
from pathlib import Path

from build123d import Align, Box, Color, Compound, Pos, export_step, export_stl

import bambu
from printers import chosen

ROOT = Path(__file__).resolve().parent.parent
GAP = 6  # between two parts on the plate
TRACE = 0.01  # mm³; less than this shared between two solids is rounding, not a clash
# Printed parts take these in turn; a bought part is green.
COLOURS = ((0.95, 0.72, 0.78), (0.6, 0.75, 0.95), (0.95, 0.95, 0.95), (0.3, 0.3, 0.3), (0.95, 0.85, 0.55))
BOUGHT = (0.25, 0.55, 0.3)
BED = (0.75, 0.75, 0.75)
BED_TILES = 16  # a side, in the plate's picture
ANGLE = (("angle.png", 35, -60, None),)  # the pictures a part has unless it names its own


def check(printed, bought):
    """Stops if a printed part is not one valid solid. Gives every pair of solids that overlap by more than a trace,
    two printed parts or a printed part and a bought one."""
    for name, shape in printed.items():
        solids = len(shape.solids())
        print(f"{name:16} {solids} solid, {shape.volume / 1000:6.1f} cm³")
        if not shape.is_valid or solids != 1:
            sys.exit(f"plate.py: {name} is not one valid solid; a piece of it is loose, or the shape is broken")
    found = []
    names = list(printed)
    for i, a in enumerate(names):
        for b, shape in [(b, printed[b]) for b in names[i + 1:]] + list(bought.items()):
            common = printed[a] & shape  # None, not an empty shape, when they share nothing
            if common is not None and common.volume > TRACE:
                found.append((a, b, common.volume))
    return found


def lay_out(printed, turn, copies, side):
    """Each printed part turned the way it prints and set on the bed, as many times as it is printed, in rows across
    a plate of that side, the deepest parts first. Stops if they do not fit."""
    on_bed = []
    for name, shape in printed.items():
        shape = turn[name] * shape if name in turn else shape
        bb = shape.bounding_box()
        shape = Pos(-bb.min.X, -bb.min.Y, -bb.min.Z) * shape
        n = copies.get(name, 1)
        on_bed += [(f"{name}_{i + 1}" if n > 1 else name, name, shape, bb.size) for i in range(n)]
    on_bed.sort(key=lambda p: -p[3].Y)  # a stable sort, so the same parts always land in the same places
    placed, x, y, row, width = [], 0, 0, 0, 0
    for label, name, shape, size in on_bed:
        if x and x + size.X > side:
            x, y, row = 0, y + row + GAP, 0
        placed.append((label, name, shape, x, y))
        x, row = x + size.X + GAP, max(row, size.Y)
        width = max(width, x - GAP)
    height = y + row
    if width > side or height > side:
        sys.exit(f"plate.py: the parts take {width:.0f} × {height:.0f} mm, more than the {side} mm plate")
    ox, oy = (side - width) / 2, (side - height) / 2
    return {label: (name, Pos(ox + x, oy + y, 0) * shape) for label, name, shape, x, y in placed}


def pictures(directory, title, printed, bought, plate, side, views):
    from preview import render

    directory.mkdir(exist_ok=True)
    colour = {name: COLOURS[i % len(COLOURS)] for i, name in enumerate(printed)}
    whole = [(shape, colour[name], 1) for name, shape in printed.items()] + [(shape, BOUGHT, 1) for shape in bought.values()]
    for file, elev, azim, caption in views:
        render(directory / file, whole, elev=elev, azim=azim, title=caption or title)
    on_plate = [(shape, colour[name], 1) for name, shape in plate.values()]
    # The bed in tiles: matplotlib orders triangles by their middles, and one as wide as the bed draws over a part on it.
    tile = side / BED_TILES
    bed = [Pos(i * tile, j * tile, -1) * Box(tile, tile, 1, align=(Align.MIN, Align.MIN, Align.MIN))
           for i in range(BED_TILES) for j in range(BED_TILES)]
    on_plate.append((Compound(bed), BED, 1))
    render(directory / "plate.png", on_plate, elev=40, azim=-60, title=f"The print plate, {side} mm")


def run(here, printed, bought=None, turn=None, copies=None, slicer=None, views=ANGLE):
    """Check a part and write its files to build/<part>/<printer>-<material>/.

    here     the part's directory; its name is the part's
    printed  the printed parts by name, each a shape where it sits when the thing is put together
    bought   the bought parts it goes round or holds, as blocks, by name; they are checked against, not printed
    turn     by printed part, the rotation that lays it the way it prints; without one it prints as modelled
    copies   by printed part, how many the plate holds; one unless named
    slicer   by printed part, what it changes from the Bambu Studio presets, by Bambu Studio's names
    views    the pictures --pictures draws beside plate.png: (file, elev, azim, caption)
    """
    bought, turn, copies, slicer = bought or {}, turn or {}, copies or {}, slicer or {}
    printer = chosen()
    if "--pictures" in sys.argv and not printer.default:
        sys.exit("plate.py: the committed pictures are drawn for the default printer and material only")
    build = ROOT / "build" / here.name / f"{printer.name}-{printer.material}"  # not committed

    found = check(printed, bought)
    plate = lay_out(printed, turn, copies, printer.plate)
    build.mkdir(parents=True, exist_ok=True)
    for old in (*build.glob("*.stl"), *build.glob("*.3mf"), *build.glob("*.step")):
        old.unlink()  # a part renamed or taken out leaves no file behind
    for label, (name, shape) in plate.items():
        export_stl(shape, build / f"{label.replace('_', '-')}.stl")
    bambu.write_project(build / "plate.3mf", [bambu.Part(label, shape, slicer.get(name, {})) for label, (name, shape) in plate.items()])

    shapes = []
    for i, (name, shape) in enumerate(printed.items()):
        shape.label, shape.color = name, Color(*COLOURS[i % len(COLOURS)])
        shapes.append(shape)
    for name, shape in bought.items():
        shape.label, shape.color = name, Color(*BOUGHT)
        shapes.append(shape)
    export_step(Compound(children=shapes, label=here.name), build / f"{here.name}.step")

    for a, b, v in found:
        print(f"clash: {a} and {b} overlap by {v:.2f} mm³")
    if found:
        sys.exit(1)
    if "--pictures" in sys.argv:
        pictures(here / "pictures", here.name.replace("-", " "), printed, bought, plate, printer.plate, views)
    calibrated = "" if printer.calibrated else ", not calibrated yet: its fits are first guesses"
    print(f"for {printer.model} ({printer.name}) in {printer.material}{calibrated}")
    size = Compound(children=list(printed.values())).bounding_box().size
    print(f"no clashes; {size.X:g} × {size.Y:g} × {size.Z:g} mm; files in {build.relative_to(ROOT)}/")
