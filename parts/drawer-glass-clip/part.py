"""drawer-glass-clip: a sleeve that connects a plate of glass to the front of a drawer.

The glass comes in from the top, into a slot. The bottom has an opening between two thin walls, up to the glass,
which runs out through the curved end: the drawer's holders slide in there. A rib runs along either side of the
opening, near its bottom edge, with room behind it for a holder to grip onto, and a patch of ridges on its underside.
One end is flat. The other end's face curves across the clip: it is full length at the side the slot is furthest from,
and sweeps back to the side the slot is nearest to.

A bracket goes with it, an angle with a web at either side. Its foot is bolted down with two M5 bolts, and its
upright leg is screwed on with four 4 mm countersunk screws. It is drawn beside the clip.

Every size is a named constant below. Coordinates: x across, toward the side the slot is nearest to, y along from the
flat end, z up from the bottom.

Run through bin/part, which checks it and writes the printable files to build/.
"""

import math
import sys
from pathlib import Path

from build123d import Align, Box, Circle, Cone, Cylinder, Plane, Polygon, Pos, Rot, extrude

# What the parts share is in lib/; put it on the path, since bin/part's PYTHONPATH is not there when this file is
# run some other way.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import plate  # noqa: E402
from printers import chosen  # noqa: E402

HERE = Path(__file__).parent
# The fits the calibration piece showed for the printer and material the build is for (printers.toml).
FITS = chosen().fits
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
SLOT_WALL = 2  # from the clip's short side to the slot, the user's measurement on the original
SLOT_FROM = 4  # from the flat end to the slot: read off the photo
SLIDE = 0.2  # a side, round the glass, across: the glass slides in
END = 0.3  # at each end of the glass, along: the glass slides in, with leeway
RIB_IN = 1  # a rib's underside, up from the bottom, the user's measurement on the original
RIB = 1.75  # a rib, from its underside to its back, the user's measurement on the original
BEHIND = 4  # the room behind a rib, between its back and the glass, the user's measurement on the original: what grips onto the rib goes there
OPENING_WALL = 1.2  # the wall on either side of the opening: three lines of the nozzle, the least a wall is; 1 mm on the original
OPENING_FROM = 14.5  # the opening and the ribs, along, from the flat end: read off the photo. They run out through the curved end
RIB_WIDE = 4  # a rib with its wall, in from the clip's side, the user's measurement on the original
RIDGE = 0.4  # how deep the grooves between the ridges are cut into a rib's underside
PITCH = 1.2  # from one groove to the next, along
RIDGES = 11  # the grooves in a rib
RIDGES_FROM = 31  # the first groove, from the flat end: read off the photo

# The bracket.
BRACKET_WIDE = 40  # the bracket, across, the user's choice
FOOT = 40  # the bracket's foot, from the upright leg's back to its front, the user's choice
UPRIGHT = 60  # the bracket's upright leg, from the foot's underside to its top, the user's choice
LEG = 6  # the foot and the upright leg, thick, the user's choice
WEB = 6  # the web at either side, between the foot and the upright leg, thick
WEB_HOLLOW = 6  # how far a web's edge curves in at its middle, from a straight line between its ends
BOLT = 5.0  # an M5 bolt's thread, ISO 4762
BOLT_APART = 14  # between the two bolts, across
BOLT_Y = 28  # the bolts, from the upright leg's back
SCREW = 4.0  # the thread of a 4 mm countersunk chipboard screw, DIN 7997
HEAD = 8.0  # that screw's head across, DIN 7997
HEAD_ANGLE = 90  # degrees, the cone under that screw's head, DIN 7997
SCREW_APART = 14  # between the two screws of a row, across
SCREW_UP = 34  # the lower row of screws, up from the foot's underside
SCREW_ROWS = 16  # from the lower row of screws to the upper row
BESIDE = 20  # between the clip and the bracket, as they are drawn

SLOT = GLASS_THICK + 2 * SLIDE  # the slot, across
SLOT_LENGTH = GLASS_EDGE + 2 * END  # the slot, along
SLOT_X = WIDTH / 2 - SLOT_WALL - SLOT / 2  # the middle of the slot and of the glass, across
FAR_WALL = WIDTH - SLOT_WALL - SLOT  # the wall on the slot's other side
OPENING = WIDTH - 2 * OPENING_WALL  # the opening, across
RIB_GAP = WIDTH - 2 * RIB_WIDE  # between the ribs
SPARE = GLASS_STOP - RIB_IN - RIB - BEHIND  # what the room behind a rib has over BEHIND, up to the glass
# The curved end's face is an arc across the clip, hollow: square to the short side where it meets it, and SWEEP
# further along at the long side.
ARC = (WIDTH**2 + SWEEP**2) / (2 * SWEEP)  # that arc's radius; its middle is this far past the end at the short side
BRACKET_X = -(WIDTH / 2 + BESIDE + BRACKET_WIDE / 2)  # the middle of the bracket, across
BOLT_HOLE = BOLT / 2 + FITS.screw_hole  # the radius of the hole a bolt slides through
SHAFT = SCREW / 2 + FITS.screw_hole  # the radius of the hole a screw slides through
SEAT = HEAD / 2 + FITS.screw_hole  # the radius of the cone seat at the upright leg's front
SEAT_DEPTH = (SEAT - SHAFT) / math.tan(math.radians(HEAD_ANGLE / 2))  # the cone seat, in from the leg's front
WEB_CHORD = math.hypot(FOOT - LEG, UPRIGHT - LEG)  # a web's edge as a straight line, from the foot's front to the leg's top
WEB_ARC = (WEB_CHORD**2 / 4 + WEB_HOLLOW**2) / (2 * WEB_HOLLOW)  # the radius of the arc a web's edge is
VIEWS = (
    *plate.ANGLE,
    ("above.png", 90, -90, "From above: the glass in its slot, and the curved end"),
    ("under.png", -35, -60, "From below: the opening, with a rib along either side"),
    ("bottom.png", -90, -90, "The bottom: the opening, the ribs and their ridges"),
    ("bracket.png", 25, 130, "The bracket: two bolts through the foot, four screws through the upright leg"),
)


def ribs():
    """The two ribs, with the ridges in their undersides: a strip along either side of the opening, near its bottom
    edge, over its whole length. They run past the curved end, whose cut ends them."""
    both = Pos(0, OPENING_FROM - JOIN, RIB_IN) * Box(OPENING + 2 * JOIN, LENGTH - OPENING_FROM + JOIN + CUT, RIB, align=FROM)
    gap = Pos(0, OPENING_FROM - CUT, RIB_IN - CUT) * Box(RIB_GAP, LENGTH - OPENING_FROM + 2 * CUT, RIB + 2 * CUT, align=FROM)
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
    # The opening goes up to the glass and out through the curved end. The clip is solid under the glass at the
    # flat end.
    opening = Pos(0, OPENING_FROM, -CUT) * Box(OPENING, LENGTH - OPENING_FROM + CUT, GLASS_STOP + CUT, align=FROM)
    # The curved end: everything inside an upright cylinder past the end is cut away.
    hollow = Pos(WIDTH / 2, LENGTH - SWEEP + ARC, -CUT) * Cylinder(ARC, DEPTH + 2 * CUT, align=MIN)
    return Box(WIDTH, LENGTH, DEPTH, align=FROM) - slot - opening + ribs() - hollow


def bracket():
    """The angle: a foot and an upright leg, with a web at either side. x across from its middle, y from the upright
    leg's back, z up from the foot's underside."""
    foot = Box(BRACKET_WIDE, FOOT, LEG, align=FROM)
    upright = Box(BRACKET_WIDE, LEG, UPRIGHT, align=FROM)
    # A web from the side: the sketch's x is the part's y, and its y the part's z. It runs from the foot's front to
    # the upright leg's top.
    side = Polygon((LEG - JOIN, LEG - JOIN), (FOOT, LEG - JOIN), (FOOT, LEG), (LEG, UPRIGHT), (LEG - JOIN, UPRIGHT), align=None)
    # Its edge is an arc, hollow, through the same two ends. The arc's middle is out past the edge, square to it
    # from its middle: (UPRIGHT - LEG, FOOT - LEG) / WEB_CHORD is that direction.
    out = WEB_ARC - WEB_HOLLOW
    middle = Pos((FOOT + LEG) / 2 + out * (UPRIGHT - LEG) / WEB_CHORD, (LEG + UPRIGHT) / 2 + out * (FOOT - LEG) / WEB_CHORD)
    web = extrude(Plane.YZ * (side - middle * Circle(WEB_ARC)), WEB)
    webs = Pos(-BRACKET_WIDE / 2, 0, 0) * web + Pos(BRACKET_WIDE / 2 - WEB, 0, 0) * web
    cuts = []
    for x in (-BOLT_APART / 2, BOLT_APART / 2):
        cuts.append(Pos(x, BOLT_Y, -CUT) * Cylinder(BOLT_HOLE, LEG + 2 * CUT, align=MIN))
    for x, z in ((x, z) for x in (-SCREW_APART / 2, SCREW_APART / 2) for z in (SCREW_UP, SCREW_UP + SCREW_ROWS)):
        # A screw goes in from the front, between the webs; -90° about x turns a shape's z to y.
        cuts.append(Pos(x, -CUT, z) * Rot(-90, 0, 0) * Cylinder(SHAFT, LEG + 2 * CUT, align=MIN))
        cuts.append(Pos(x, LEG - SEAT_DEPTH, z) * Rot(-90, 0, 0) * Cone(SHAFT, SEAT, SEAT_DEPTH, align=MIN))
    whole = foot + upright + webs
    for cut in cuts:
        whole -= cut
    return Pos(BRACKET_X, 0, 0) * whole


def glass():
    """The glass, as a block: the edge that stands in the slot, and the start of the pane above it."""
    return Pos(SLOT_X, SLOT_FROM + END, GLASS_STOP) * Box(GLASS_THICK, GLASS_EDGE, GLASS_SHOWN, align=FROM)


def main():
    # The clip prints standing on its flat end, so every layer is a ring or a U round the glass, and the glass cannot
    # split the walls off. The slot's far end bridges from wall to wall. A brim keeps the tall piece on the
    # plate.
    # The bracket prints lying on its side, so every layer is the whole angle and the load does not split the legs
    # apart. The web on top hangs over the room between the webs, so it prints on supports.
    plate.run(
        HERE,
        printed={"clip": clip(), "bracket": bracket()},
        bought={"glass": glass()},
        turn={"clip": Rot(90, 0, 0), "bracket": Rot(0, 90, 0)},
        slicer={"clip": {"brim_type": "outer_only", "brim_width": "5"}, "bracket": {"enable_support": "1"}},
        views=VIEWS,
    )


if __name__ == "__main__":
    main()
