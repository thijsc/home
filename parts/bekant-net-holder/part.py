"""bekant-net-holder: a holder for the IKEA Bekant's cable net, in place of IKEA's part 130884.

A plug with barbs goes into a hole under the desk, and its flange holds a loop of the net. A pin goes into the plug
from below and keeps its four prongs apart, so the barbs stay in the hole.

Every size is a named constant below. Coordinates: x and y across, z up from the flange's rim, the plug's face that
lies on the plate. Under the desk the whole thing hangs the other way up.

Run through bin/part, which checks it and writes the printable files to build/.
"""

import sys
from pathlib import Path

from build123d import Align, Axis, Box, Circle, Cone, Cylinder, Plane, Pos, Rectangle, Rot, make_hull, revolve

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

# The plug. Its sizes are the ones of a print that fits the desk's hole.
FLANGE = 18  # the flange across, where it lies against the desk
RIM = 16  # the flange across at its rim, the edge away from the desk: its side slopes
FLANGE_THICK = 2  # the flange, from its rim to the desk
RECESS = 1  # the recess inside the rim, deep; the pin's head sits in it
RECESS_FLOOR = 14  # that recess across at its floor: it widens to RIM at the rim
COLLAR = 9.5  # the round shaft across, next to the flange
COLLAR_HEIGHT = 3  # that shaft, up from the flange
NECK = 8.8  # the shaft across between the collar and the first barb
NECK_HEIGHT = 1  # that neck, up from the collar
BARB = 10  # a barb across at its wide end, which faces the flange
BARB_ROOT = 7.6  # a barb across at its narrow end
BARB_PITCH = 1.2  # a barb, up
BARBS = 6
TIP = 7  # the prongs across at their end
TIP_HEIGHT = 1.5  # the last barb, which narrows to TIP
HOLE = 4  # the hole through the plug, which the pin goes into
SLOT = 1  # each of the two slots that split the shaft into four prongs, wide

# The pin.
HEAD = 12  # the pin's head across
HEAD_THICK = 2.3  # the head, from its outer face to the face that lies in the recess
HEAD_EDGE = 0.3  # the head's side is straight this far up from its outer face, then slopes in
HEAD_FLAT = 8.76  # the head's face in the recess, across its flat
HEAD_ROUND = 1  # the radius the head's side rounds over with to that face
PIN = HOLE - 2 * FITS.printed_grip  # the pin's shaft across: it pushes into the hole and holds
PIN_LENGTH = 14.9  # the shaft, from the head to its end
PIN_TIP = 0.5  # the shaft narrows this much at its end, over as much length, so it finds the hole

RECESS_SLOPE = (RIM - RECESS_FLOOR) / 2 / RECESS  # how much the recess widens for every mm toward the rim
COLLAR_Z = FLANGE_THICK  # where the collar starts
NECK_Z = COLLAR_Z + COLLAR_HEIGHT  # where the neck starts, and the slots
BARB_Z = NECK_Z + NECK_HEIGHT  # where the first barb starts
TIP_Z = BARB_Z + BARBS * BARB_PITCH  # where the last barb starts
TOP = TIP_Z + TIP_HEIGHT  # the prongs' end
HEAD_Z = RECESS - HEAD_THICK  # the head's outer face, which is below the rim
VIEWS = (
    *plate.ANGLE,
    ("under.png", -30, -60, "From the side of the room: the pin's head in the flange's recess"),
    ("side.png", 0, -90, "From the side: the barbs, and a slot between two prongs"),
)


def slot():
    """A slot across the whole shaft, from the collar to the prongs' end, round at its bottom."""
    across = BARB + 2 * CUT
    bottom = NECK_Z + SLOT / 2  # the middle of the round bottom
    cut = Pos(0, 0, bottom) * Box(SLOT, across, TOP + CUT - bottom, align=MIN)
    return cut + Pos(0, 0, bottom) * Rot(90, 0, 0) * Cylinder(SLOT / 2, across)


def plug():
    flange = Cone(RIM / 2, FLANGE / 2, FLANGE_THICK, align=MIN)
    recess = Pos(0, 0, -CUT) * Cone(RIM / 2 + CUT * RECESS_SLOPE, RECESS_FLOOR / 2, RECESS + CUT, align=MIN)
    shaft = Pos(0, 0, COLLAR_Z) * Cylinder(COLLAR / 2, COLLAR_HEIGHT, align=MIN)
    shaft += Pos(0, 0, NECK_Z) * Cylinder(NECK / 2, NECK_HEIGHT, align=MIN)
    for i in range(BARBS):
        shaft += Pos(0, 0, BARB_Z + i * BARB_PITCH) * Cone(BARB / 2, BARB_ROOT / 2, BARB_PITCH, align=MIN)
    shaft += Pos(0, 0, TIP_Z) * Cone(BARB / 2, TIP / 2, TIP_HEIGHT, align=MIN)
    hole = Pos(0, 0, -CUT) * Cylinder(HOLE / 2, TOP + 2 * CUT, align=MIN)
    return flange + shaft - recess - hole - slot() - Rot(0, 0, 90) * slot()


def head_profile():
    """Half the head from the side: x from its middle, and the sketch's y is up from its outer face."""
    edge = Rectangle(HEAD / 2, HEAD_EDGE, align=Align.MIN)
    middle = Rectangle(HEAD_FLAT / 2, HEAD_THICK, align=Align.MIN)
    # The side runs straight from the edge to this round, which ends in the flat face.
    corner = Pos(HEAD_FLAT / 2, HEAD_THICK - HEAD_ROUND) * Circle(HEAD_ROUND)
    return make_hull((edge + middle + corner).edges())


def pin():
    head = Pos(0, 0, HEAD_Z) * revolve(Plane.XZ * head_profile(), Axis.Z)
    straight = HEAD_THICK + PIN_LENGTH - PIN_TIP  # the shaft starts at the head's outer face, inside the head
    shaft = Pos(0, 0, HEAD_Z) * Cylinder(PIN / 2, straight, align=MIN)
    tip = Pos(0, 0, HEAD_Z + straight) * Cone(PIN / 2, PIN / 2 - PIN_TIP, PIN_TIP, align=MIN)
    return head + shaft + tip


def main():
    # The recess's floor hangs over the plate, so it prints on supports. They stand on the plate only: the barbs'
    # flat faces are 1.2 mm ledges and print without.
    supports = {"enable_support": "1", "support_on_build_plate_only": "1"}
    plate.run(HERE, printed={"plug": plug(), "pin": pin()}, slicer={"plug": supports}, views=VIEWS)


if __name__ == "__main__":
    main()
