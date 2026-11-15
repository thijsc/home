"""drawer-clamp: a clamp that keeps a drawer shut, on the outside of the cupboard's side.

A base is screwed to the outside of the cupboard's side, from its front edge back. Its plate has a knuckle on it at
the top and the bottom of its back, and an M5 bolt stands upright through both. An arm turns on the bolt, with its knuckle
between the base's two. The arm is an angle: one leg lies along the side, over the base, and the other goes round
the corner and across the drawer's front. It swings out sideways to let the drawer go. The bolt's head is sunk in the upper knuckle and its
locknut in a pocket in the lower one, both level with the outside, and the bolt is tightened until the arm turns stiffly.

Every size is a named constant below. Coordinates: x across from the outside of the cupboard's side, toward the
drawer, y deep from the front of the side and the drawer, into the cupboard, z up from the base's underside.

Run through bin/part, which checks it and writes the printable files to build/.
"""

import math
import sys
from pathlib import Path

from build123d import Align, Box, Circle, Cone, Cylinder, Pos, Rectangle, RegularPolygon, Rot, extrude

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
CORNER = (Align.MIN, Align.MIN)  # a rectangle placed by its corner nearest the side's outside and the front
BLOCK = (Align.MIN, Align.MIN, Align.MIN)

SIDE = 50  # the cupboard's side, thick, the user's measurement
REACH = 100  # the arm's end, across, from the outside of the cupboard's side, the user's choice
LENGTH = 75  # the base, from the front of the side back
LUG = 10  # each of the base's two knuckles, at its top and its bottom, up
GRIP = 0.05  # between the arm's knuckle and each of the base's: less than a sliding fit, so the bolt closes the base's knuckles onto the arm's and the arm turns stiffly
CLEAR = 0.5  # between the arm and what it lies along or turns past: the side, the drawer's front and the base
PLATE = 6  # the base's plate against the cupboard's side, thick
KNUCKLE = 14  # a knuckle of the hinge, across
BOLT = 5.0  # an M5 socket cap bolt's thread, ISO 4762
BOLT_LENGTH = 30  # that bolt, under its head: 35 mm with its head, the user's measurement
BOLT_HEAD = 8.5  # that bolt's round head, across, ISO 4762
BOLT_HEAD_HIGH = 5.0  # that bolt's head, ISO 4762
HEAD_ROOM = 0.5  # a side, round the bolt's head in its hole: the head turns in it
NUT = 8.0  # an M5 locknut, across the flats, DIN 985
NUT_HIGH = 5.0  # that nut, DIN 985
SCREW = 4.0  # the thread of a 4 mm countersunk chipboard screw, DIN 7997
HEAD = 8.0  # that screw's head across, DIN 7997
HEAD_ANGLE = 90  # degrees, the cone under that screw's head, DIN 7997
SCREW_FROM = 10  # the first screw, from the base's front
SCREW_APART = 40  # between the two screws, front to back
END_ROUND = 4  # the radius of the two upright corners at the arm's end
TIP = 1.2  # the least the leg is thick where it runs out round the base's knuckles: three lines of the nozzle
SHOWN = 15  # how far the pictures show the cupboard's side and the drawer's front past the clamp
DRAWER_SHOWN = 18  # how thick the pictures show the drawer's front: it is not measured

HEIGHT = BOLT_LENGTH + BOLT_HEAD_HIGH  # the base and the arm, up: the bolt with its head, so its head is level with the top and its end with the underside
RADIUS = KNUCKLE / 2  # a knuckle's radius
ARM = KNUCKLE  # the arm's two legs, thick: as thick as its knuckle is across, so the leg's two faces run on from the knuckle's
BOLT_X = -(PLATE + CLEAR + RADIUS)  # the bolt, across: the arm's knuckle turns CLEAR from the base's plate
BOLT_Y = LENGTH - RADIUS  # the bolt, deep: the knuckles end with the base's back
OUTSIDE = BOLT_X - RADIUS  # the hinge's far side, across, from the cupboard's side
ARM_LOW = LUG + GRIP  # the underside of the arm's knuckle, up
ARM_HIGH = HEIGHT - LUG - GRIP  # the top of the arm's knuckle, up
ROUND = ARM  # the radius of the arm's outside corner, about its inside corner: the arm keeps its thickness round it
LEG_END = BOLT_Y - RADIUS - CLEAR  # where the arm's leg along the side ends at its full height, before the base's knuckles
# On the outside the leg goes on round the knuckles, hollow, CLEAR from their round side, up to where it is TIP thick.
TIP_END = BOLT_Y - math.sqrt((RADIUS + CLEAR) ** 2 - (RADIUS - TIP) ** 2)
ARM_IN = -PLATE - CLEAR  # the inside of the arm's leg along the side, which faces the base's plate
ARM_BACK = -CLEAR  # the back of the arm's leg across the front, which faces the side's front edge and the drawer's front
HEAD_SINK = BOLT_HEAD_HIGH  # the hole for the bolt's head, down from the base's top: the head is level with the top
NUT_SINK = NUT_HIGH  # the pocket for the nut, up from the base's underside: the nut is level with the underside, and so is the bolt's end
HEAD_HOLE = BOLT_HEAD / 2 + HEAD_ROOM  # the radius of the hole for the bolt's head
NUT_POCKET = NUT / 2 + FITS.nut_pocket  # half the nut's pocket across its flats: the nut presses in and does not turn
BOLT_HOLE = BOLT / 2 + FITS.screw_hole  # the radius of the hole the bolt slides through, and the arm turns on
SHAFT = SCREW / 2 + FITS.screw_hole  # the radius of the hole a screw slides through
SEAT = HEAD / 2 + FITS.screw_hole  # the radius of the cone seat at the plate's outside
SEAT_DEPTH = (SEAT - SHAFT) / math.tan(math.radians(HEAD_ANGLE / 2))  # the cone seat, in from the plate's outside
VIEWS = (
    ("angle.png", 30, -125, None),
    ("above.png", 90, -90, "From above: the arm closed, round the corner of the cupboard's side"),
    ("side.png", 15, 170, "From the side: the arm's leg over the base, and the bolt's head sunk in the upper knuckle"),
    ("under.png", -40, 160, "From below: the locknut in its pocket in the lower knuckle"),
    ("back.png", 20, -160, "From behind: the base's knuckles above and below the arm's"),
)


def bolt_hole():
    return Pos(BOLT_X, BOLT_Y, -CUT) * Cylinder(BOLT_HOLE, HEIGHT + 2 * CUT, align=MIN)


def base():
    """The plate against the cupboard's side, with a knuckle on it at the top and the bottom of its back. A knuckle
    is square where it stands on the plate and round on the outside, about the bolt."""
    whole = Box(PLATE, LENGTH, HEIGHT, align=(Align.MAX, Align.MIN, Align.MIN))
    knuckle = Pos(BOLT_X, BOLT_Y) * Circle(RADIUS) + Pos(BOLT_X, BOLT_Y - RADIUS) * Rectangle(-BOLT_X, KNUCKLE, align=CORNER)
    for z in (0, HEIGHT - LUG):
        whole += Pos(0, 0, z) * extrude(knuckle, LUG)
    whole -= bolt_hole()
    whole -= Pos(BOLT_X, BOLT_Y, HEIGHT - HEAD_SINK) * Cylinder(HEAD_HOLE, HEAD_SINK + CUT, align=MIN)
    # The nut's pocket has a flat toward the plate and one away from it, so on the plate its top is a flat bridge.
    hexagon = Rot(0, 0, 30) * RegularPolygon(NUT_POCKET, 6, major_radius=False)
    whole -= Pos(BOLT_X, BOLT_Y, -CUT) * extrude(hexagon, NUT_SINK + CUT)
    for y in (SCREW_FROM, SCREW_FROM + SCREW_APART):
        # A screw goes in from the outside, into the cupboard's side; 90° about y turns a shape's z to x.
        whole -= Pos(-PLATE - CUT, y, HEIGHT / 2) * Rot(0, 90, 0) * Cylinder(SHAFT, PLATE + 2 * CUT, align=MIN)
        whole -= Pos(-PLATE, y, HEIGHT / 2) * Rot(0, 90, 0) * Cone(SEAT, SHAFT, SEAT_DEPTH, align=MIN)
    return whole


def arm():
    """An angle, as high as the base: a leg along the cupboard's side, from the base's knuckles to the front, and a
    leg across the front, square to it, with a round outside corner. At the knuckles the leg's end is hollow on the
    outside, round the base's knuckles. The knuckle sits between the base's two, and a neck as thick as the leg
    joins it to the leg's end."""
    # The leg along the side runs to TIP_END. A circle about the bolt hollows its end round the base's knuckles, and
    # the half toward the cupboard is cut back to LEG_END, before the knuckles' square side.
    legs = (
        Pos(ARM_IN - ARM, ARM_BACK - ARM) * Rectangle(ARM, TIP_END - ARM_BACK + ARM, align=CORNER)
        - Pos(BOLT_X, BOLT_Y) * Circle(RADIUS + CLEAR)
        - Pos(BOLT_X, LEG_END) * Rectangle(RADIUS + CUT, TIP_END - LEG_END + CUT, align=CORNER)
        + Pos(ARM_IN - ARM, ARM_BACK - ARM) * Rectangle(REACH - ARM_IN + ARM, ARM, align=CORNER)
    )
    # The outside corner is round: what is outside a circle about the inside corner is cut from the corner's square.
    legs -= Pos(ARM_IN - ARM - CUT, ARM_BACK - ARM - CUT) * Rectangle(ROUND + CUT, ROUND + CUT, align=CORNER) - Pos(ARM_IN, ARM_BACK) * Circle(ROUND)
    # So are the two corners at the arm's end, the one at the drawer's front and the one away from it.
    for y, toward in ((ARM_BACK, -1), (ARM_BACK - ARM, 1)):
        square = Pos(REACH - END_ROUND / 2 + CUT / 2, y + toward * (END_ROUND - CUT) / 2) * Rectangle(END_ROUND + CUT, END_ROUND + CUT)
        legs -= square - Pos(REACH - END_ROUND, y + toward * END_ROUND) * Circle(END_ROUND)
    knuckle = Pos(BOLT_X, BOLT_Y) * Circle(RADIUS) + Pos(ARM_IN - ARM, LEG_END - JOIN) * Rectangle(ARM, BOLT_Y - LEG_END + JOIN, align=CORNER)
    return extrude(legs, HEIGHT) + Pos(0, 0, ARM_LOW) * extrude(knuckle, ARM_HIGH - ARM_LOW) - bolt_hole()


def bolt():
    """The bolt with its head sunk in the base's upper knuckle and the locknut in its pocket in the lower one, as
    cylinders."""
    return (
        Pos(BOLT_X, BOLT_Y, HEIGHT - HEAD_SINK - BOLT_LENGTH) * Cylinder(BOLT / 2, BOLT_LENGTH, align=MIN)
        + Pos(BOLT_X, BOLT_Y, HEIGHT - HEAD_SINK) * Cylinder(BOLT_HEAD / 2, BOLT_HEAD_HIGH, align=MIN)
        + Pos(BOLT_X, BOLT_Y, NUT_SINK - NUT_HIGH) * Cylinder(NUT / 2, NUT_HIGH, align=MIN)
    )


def side():
    """The cupboard's side, as a block: its front edge, as far back as the base goes."""
    return Pos(0, 0, -SHOWN) * Box(SIDE, BOLT_Y + RADIUS + SHOWN, HEIGHT + 2 * SHOWN, align=BLOCK)


def drawer():
    """The drawer's front, as a block: flush with the front of the side, and on past the arm's end."""
    return Pos(SIDE, 0, -SHOWN) * Box(REACH - SIDE + SHOWN, DRAWER_SHOWN, HEIGHT + 2 * SHOWN, align=BLOCK)


def main():
    # The base prints on its back, the face that lies against the cupboard. The knuckles stand up from the plate,
    # round on top, and the screws' holes are upright. The knuckles' layers lie across them: the bolt bends each
    # one GRIP at most before it rests on the arm's knuckle.
    # The arm prints lying as it sits, so every layer is the whole angle, and the drawer's push bends it along the
    # layers. Its knuckle and the neck to it hang LUG above the plate, so they print on supports.
    plate.run(
        HERE,
        printed={"base": base(), "arm": arm()},
        bought={"bolt": bolt(), "side": side(), "drawer": drawer()},
        turn={"base": Rot(0, 90, 0)},
        slicer={"arm": {"enable_support": "1"}},
        views=VIEWS,
    )


if __name__ == "__main__":
    main()
