"""door-switch-clamp: a clamp that holds the door switch, which turns the light on when the door opens, and covers
its wires.

The case goes over the switch and is screwed down through a wing on either side. The switch's front stays open, flush
with the case's front, for the door. Behind the switch the case covers a room for the wires, which is open at the
back over its whole width and height.

Every size is a named constant below. Coordinates: x across, y deep from the open front to the back, z up from the
surface the switch is mounted on.

Run through bin/part, which checks it and writes the printable files to build/.
"""

import math
import sys
from pathlib import Path

from build123d import Align, Axis, Box, Circle, Cone, Cylinder, Plane, Polygon, Pos, Rectangle, Rot, extrude, mirror, revolve

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

SWITCH_WIDTH = 31  # the switch, across, the user's measurement
SWITCH_DEPTH = 30  # the switch, front to back, its round back included, the user's measurement
SWITCH_HEIGHT = 8  # the switch, up from the surface, the user's measurement
SLIDE = 0.2  # a side, round the switch and over it: the case slides over it
WALL = 5  # the case's side walls and its top
WIRE_ROOM = 15  # the room behind the switch for its wires, front to back, open at the back
WIRE_ROOF = 2  # the case's top over the wire room, which is higher than the pocket; it carries no load
EDGE = 1.2  # the least the top is thick at the wire room's opening, where the top rounds over: three lines of the nozzle
SLOPE = 45  # degrees from upright, the steepest the inside closes in at, so it prints standing without supports
TOP_ROUND = 3  # the radius the case's top rounds over to its sides with
WING_THICK = 5  # a wing, up from the surface
WING_RIM = 3  # the wing round the screw's head
SCREW = 4.0  # the thread of a 4 mm countersunk chipboard screw, DIN 7997
HEAD = 8.0  # that screw's head across, DIN 7997
HEAD_ANGLE = 90  # degrees, the cone under that screw's head, DIN 7997

POCKET = SWITCH_WIDTH / 2 + SLIDE  # half the pocket the switch sits in, and the radius of its round back
POCKET_Y = SWITCH_DEPTH - SWITCH_WIDTH / 2  # the middle of the switch's round back, front to back
INSIDE = SWITCH_HEIGHT + SLIDE  # the pocket and the wire room, up from the surface
HALF = POCKET + WALL  # half the case across, and the radius of its round back
HEIGHT = INSIDE + WALL  # the case's top
BACK = SWITCH_DEPTH + SLIDE + WIRE_ROOM  # the case's back, where the wire room is open
ROUND_Y = BACK - HALF  # the middle of the case's round back, front to back
# The wire room is narrower than the switch, so the pocket's round back stays as a shoulder on either side that the
# switch's back rests against. It is as wide as it can be with that shoulder no steeper than SLOPE.
WIRE_HALF = POCKET * math.cos(math.radians(SLOPE))
WIRE_INSIDE = HEIGHT - WIRE_ROOF  # the wire room's ceiling, up from the surface
RISE_Y = SWITCH_DEPTH + SLIDE  # where the ceiling starts to rise from the pocket's to the wire room's, behind the switch
RISE = (WIRE_INSIDE - INSIDE) / math.tan(math.radians(SLOPE))  # how far back it rises over, at SLOPE
# The case's top rounds over at the back, so it thins toward its edge over the wire room. The top ends over the
# opening where it is EDGE thick, this far from the middle of the case's round back.
EDGE_AT = HALF - TOP_ROUND + math.sqrt(TOP_ROUND**2 - (WIRE_INSIDE + EDGE - (HEIGHT - TOP_ROUND)) ** 2)
FILLET = HEIGHT - WING_THICK - TOP_ROUND  # the radius the case's side curves down to a wing with
WING_DEPTH = HEAD + 2 * WING_RIM  # a wing, front to back
SCREW_X = HALF + FILLET + WING_DEPTH / 2  # a screw, from the middle of the case
SCREW_Y = WING_DEPTH / 2  # a screw, from the front
WING_END = SCREW_X + WING_DEPTH / 2  # a wing's end, from the middle of the case
SHAFT = SCREW / 2 + FITS.screw_hole  # the radius of the hole a screw slides through
SEAT = HEAD / 2 + FITS.screw_hole  # the radius of the cone seat at the wing's top
SEAT_DEPTH = (SEAT - SHAFT) / math.tan(math.radians(HEAD_ANGLE / 2))  # the cone seat, down from the wing's top
VIEWS = (
    *plate.ANGLE,
    ("under.png", -35, -60, "From below: the switch in its pocket, and the wire room behind it, open at the back"),
    ("front.png", 0, -90, "From the front: the case curves down to the wings"),
    ("back.png", 20, 110, "From behind: the wire room's opening"),
)


def upright(sketch, y_from, y_to):
    """A sketch of a section, x across and the sketch's y the part's z, made a solid from y_from to y_to."""
    return Pos(0, y_to, 0) * Rot(90, 0, 0) * extrude(sketch, y_to - y_from)


def section():
    """The right half of the case from the front: square at the surface, round at the top."""
    low = Rectangle(HALF, HEIGHT - TOP_ROUND, align=Align.MIN)
    high = Rectangle(HALF - TOP_ROUND, HEIGHT, align=Align.MIN)
    return low + high + Pos(HALF - TOP_ROUND, HEIGHT - TOP_ROUND) * Circle(TOP_ROUND)


def shell():
    """The case, solid: straight along the switch, and round behind it like the switch's back."""
    right = upright(section(), 0, ROUND_Y)
    back = Pos(0, ROUND_Y, 0) * revolve(Rot(90, 0, 0) * section(), Axis.Z, 180)
    return right + mirror(right, Plane.YZ) + back


def wing():
    """The right wing, at the front: flat round the screw, and a curve from the case's side down to it."""
    flat = Pos(HALF - JOIN, 0) * Rectangle(WING_END - HALF + JOIN, WING_THICK, align=Align.MIN)
    corner = Pos(HALF - JOIN, WING_THICK - JOIN) * Rectangle(FILLET + JOIN, FILLET + JOIN, align=Align.MIN)
    curve = corner - Pos(HALF + FILLET, WING_THICK + FILLET) * Circle(FILLET)
    # From above the wing is square at the front, which lies on the plate, and round at its back outer corner.
    outline = (
        Pos(HALF - JOIN, 0) * Rectangle(SCREW_X - HALF + JOIN, WING_DEPTH, align=Align.MIN)
        + Pos(SCREW_X - JOIN, 0) * Rectangle(WING_DEPTH / 2 + JOIN, SCREW_Y, align=Align.MIN)
        + Pos(SCREW_X, SCREW_Y) * Circle(WING_DEPTH / 2)
    )
    solid = upright(flat + curve, 0, WING_DEPTH) & extrude(outline, HEIGHT)
    hole = Pos(SCREW_X, SCREW_Y, -CUT) * Cylinder(SHAFT, WING_THICK + 2 * CUT, align=MIN)
    seat = Pos(SCREW_X, SCREW_Y, WING_THICK - SEAT_DEPTH) * Cone(SHAFT, SEAT, SEAT_DEPTH, align=MIN)
    return solid - hole - seat


def inside():
    """What the case is hollow for: the pocket the switch sits in, and the wire room behind it, which runs out
    through the case's back and is higher than the pocket."""
    pocket = Pos(0, -CUT) * Rectangle(2 * POCKET, POCKET_Y + CUT, align=(Align.CENTER, Align.MIN)) + Pos(0, POCKET_Y) * Circle(POCKET)
    room = Pos(0, POCKET_Y) * Rectangle(2 * WIRE_HALF, BACK + CUT - POCKET_Y, align=(Align.CENTER, Align.MIN))
    hollow = Pos(0, 0, -CUT) * extrude(pocket + room, INSIDE + CUT)
    # The ceiling rises behind the switch at SLOPE, so it prints standing without supports. From the side: the
    # sketch's x is the part's y, and its y the part's z.
    side = Polygon(
        (RISE_Y, INSIDE - CUT), (RISE_Y, INSIDE), (RISE_Y + RISE, WIRE_INSIDE),
        (BACK + CUT, WIRE_INSIDE), (BACK + CUT, INSIDE - CUT),
        align=None,
    )
    high = extrude(Plane.YZ * side, WIRE_HALF, both=True)
    # The top's thin edge over the opening: everything past EDGE_AT, as wide as the wire room.
    past = Pos(0, ROUND_Y, -CUT) * (
        Box(2 * WIRE_HALF, HALF + CUT, HEIGHT + 2 * CUT, align=(Align.CENTER, Align.MIN, Align.MIN))
        - Cylinder(EDGE_AT, HEIGHT + 2 * CUT, align=MIN)
    )
    return hollow + high + past


def clamp():
    right = wing()
    return shell() + right + mirror(right, Plane.YZ) - inside()


def switch():
    """The switch, as a block of its outline: straight at the front, a half circle at the back."""
    front = Rectangle(SWITCH_WIDTH, POCKET_Y, align=(Align.CENTER, Align.MIN))
    return extrude(front + Pos(0, POCKET_Y) * Circle(SWITCH_WIDTH / 2), SWITCH_HEIGHT)


def main():
    # The clamp prints standing on its open front, so the inside needs no supports.
    plate.run(HERE, printed={"clamp": clamp()}, bought={"switch": switch()}, turn={"clamp": Rot(90, 0, 0)}, views=VIEWS)


if __name__ == "__main__":
    main()
