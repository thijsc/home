"""drawer-glass-clip: a sleeve that connects a plate of glass to the front of a drawer.

The glass comes in from the top, into a slot. The bottom has an opening between two thin walls, up to the glass,
which a part of the drawer comes up into. A rib runs along either side of the opening, near its bottom edge, with
room behind it for that part to grip onto, and a patch of ridges on its underside. One end is flat. The other end's face
curves across the clip: it is full length at the side the slot is nearest to, and sweeps back to the other side.

Every size is a named constant below. Coordinates: x across, toward the side the slot is nearest to, y along from the
flat end, z up from the bottom.

Run through bin/part, which checks it and writes the printable files to build/.
"""

import sys
from pathlib import Path

from build123d import Align, Box, Cylinder, Plane, Polygon, Pos, Rot, extrude

# What the parts share is in lib/; put it on the path, since bin/part's PYTHONPATH is not there when this file is
# run some other way.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import plate  # noqa: E402

HERE = Path(__file__).parent
CUT = 1  # a cut runs this far past what it cuts through, so it leaves no skin
JOIN = 1  # a shape added to another runs this far into it, so the two are one solid
MIN = (Align.CENTER, Align.CENTER, Align.MIN)
FROM = (Align.CENTER, Align.MIN, Align.MIN)  # a box placed by the middle of its width, its near end and its underside

LENGTH = 100  # the clip, along, at its longest side, the user's measurement on the original
WIDTH = 15.10  # the clip, across, the user's measurement on the original
DEPTH = 35  # the clip, from the bottom to the top: read off the user's photo of the original on a cutting mat
SWEEP = 2  # how far the curved end's face is back at its short side, the user's measurement on the original
GLASS_THICK = 8  # the glass, across, the user's measurement
GLASS_EDGE = 89  # the edge of the glass that stands in the slot, along, the user's measurement
GLASS_SHOWN = 45  # how much of the glass the pictures show, up from the slot's floor: the pane goes on above it
GLASS_STOP = 7  # from the bottom to the glass, the user's measurement on the original
SLOT_WALL = 2  # from the clip's long side to the slot, the user's measurement on the original
SLOT_FROM = 4  # from the flat end to the slot: read off the photo
SLIDE = 0.2  # a side and an end, round the glass: the glass slides in
RIB_IN = 1  # a rib's underside, up from the bottom, the user's measurement on the original
RIB = 1.75  # a rib, from its underside to its back, the user's measurement on the original
BEHIND = 4  # the room behind a rib, between its back and the glass, the user's measurement on the original: what grips onto the rib goes there
OPENING_WALL = 1.2  # the wall on either side of the opening: three lines of the nozzle, the least a wall is; 1 mm on the original
OPENING_FROM = 14.5  # the opening and the ribs, along, from the flat end: read off the photo
OPENING_TO = 70  # where the opening and the ribs end, from the flat end, the user's measurement on the original
RIB_WIDE = 4  # a rib with its wall, in from the clip's side, the user's measurement on the original
RIDGE = 0.4  # how deep the grooves between the ridges are cut into a rib's underside
PITCH = 1.2  # from one groove to the next, along
RIDGES = 11  # the grooves in a rib
RIDGES_FROM = 31  # the first groove, from the flat end: read off the photo

SLOT = GLASS_THICK + 2 * SLIDE  # the slot, across
SLOT_LENGTH = GLASS_EDGE + 2 * SLIDE  # the slot, along
SLOT_X = WIDTH / 2 - SLOT_WALL - SLOT / 2  # the middle of the slot and of the glass, across
FAR_WALL = WIDTH - SLOT_WALL - SLOT  # the wall on the slot's other side
OPENING = WIDTH - 2 * OPENING_WALL  # the opening, across
RIB_GAP = WIDTH - 2 * RIB_WIDE  # between the ribs
SPARE = GLASS_STOP - RIB_IN - RIB - BEHIND  # what the room behind a rib has over BEHIND, up to the glass
# The curved end's face is an arc across the clip, hollow: square to the short side where it meets it, and SWEEP
# further along at the long side.
ARC = (WIDTH**2 + SWEEP**2) / (2 * SWEEP)  # that arc's radius; its middle is this far past the end at the short side
VIEWS = (
    *plate.ANGLE,
    ("above.png", 90, -90, "From above: the glass in its slot, and the curved end"),
    ("under.png", -35, -60, "From below: the opening, with a rib along either side"),
    ("bottom.png", -90, -90, "The bottom: the opening, the ribs and their ridges"),
)


def ribs():
    """The two ribs, with the ridges in their undersides: a strip along either side of the opening, near its bottom
    edge, over its whole length."""
    both = Pos(0, OPENING_FROM - JOIN, RIB_IN) * Box(OPENING + 2 * JOIN, OPENING_TO - OPENING_FROM + 2 * JOIN, RIB, align=FROM)
    gap = Pos(0, OPENING_FROM - CUT, RIB_IN - CUT) * Box(RIB_GAP, OPENING_TO - OPENING_FROM + 2 * CUT, RIB + 2 * CUT, align=FROM)
    # The grooves, from the side: the sketch's x is the part's y, and its y the part's z. What is left between two
    # grooves is a ridge, with its tip at the rib's underside.
    one = Polygon((0, -CUT), (0, 0), (PITCH / 2, RIDGE), (PITCH, 0), (PITCH, -CUT), align=None)
    row = one
    for i in range(1, RIDGES):
        row += Pos(i * PITCH, 0) * one
    grooves = Pos(0, RIDGES_FROM, RIB_IN) * extrude(Plane.YZ * row, OPENING / 2, both=True)
    return both - gap - grooves


def clip():
    slot = Pos(SLOT_X, SLOT_FROM, GLASS_STOP) * Box(SLOT, SLOT_LENGTH, DEPTH - GLASS_STOP + CUT, align=FROM)
    # The opening goes up to the glass. The clip is solid under the glass on either side of it, along.
    opening = Pos(0, OPENING_FROM, -CUT) * Box(OPENING, OPENING_TO - OPENING_FROM, GLASS_STOP + CUT, align=FROM)
    # The curved end: everything inside an upright cylinder past the end is cut away.
    hollow = Pos(-WIDTH / 2, LENGTH - SWEEP + ARC, -CUT) * Cylinder(ARC, DEPTH + 2 * CUT, align=MIN)
    return Box(WIDTH, LENGTH, DEPTH, align=FROM) - slot - opening + ribs() - hollow


def glass():
    """The glass, as a block: the edge that stands in the slot, and the start of the pane above it."""
    return Pos(SLOT_X, SLOT_FROM + SLIDE, GLASS_STOP) * Box(GLASS_THICK, GLASS_EDGE, GLASS_SHOWN, align=FROM)


def main():
    # The clip prints standing on its flat end, so every layer is a ring or a U round the glass, and the glass cannot
    # split the walls off. The slot's and the opening's far ends bridge from wall to wall. A brim keeps the tall
    # piece on the plate.
    plate.run(
        HERE,
        printed={"clip": clip()},
        bought={"glass": glass()},
        turn={"clip": Rot(90, 0, 0)},
        slicer={"clip": {"brim_type": "outer_only", "brim_width": "5"}},
        views=VIEWS,
    )


if __name__ == "__main__":
    main()
