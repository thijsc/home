"""bekant-net-holder: a holder for the IKEA Bekant's cable net, in place of IKEA's part 130884.

A plug with barbs goes into a hole under the desk, and its flange holds a loop of the net. A pin goes into the plug
from below and pushes its four prongs apart, so the barbs press into the hole's wall.

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

HERE = Path(__file__).parent
CUT = 1  # a cut runs this far past what it cuts through, so it leaves no skin
MIN = (Align.CENTER, Align.CENTER, Align.MIN)

# The pin. Its sizes are measured on the model of a pin that fits, Ikea Bekant Cable Holder Pin.stl.
HEAD = 12  # the pin's head across
HEAD_THICK = 2.3  # the head, from its outer face to the face that lies in the recess
HEAD_EDGE = 0.3  # the head's side is straight this far up from its outer face, then slopes in
HEAD_FLAT = 8.76  # the head's face in the recess, across its flat
HEAD_ROUND = 1  # the radius the head's side rounds over with to that face
THINNER = 0.2  # the shaft is this much thinner than the model's, which is too thick for the printed plug's hole
PIN = 4.75 - THINNER  # the pin's shaft across
PIN_ROOT = 0.75  # the radius the shaft rounds out with into the head
PIN_LENGTH = 14.9  # the shaft, from the head to its end
PIN_STRAIGHT = 11.3  # the shaft is PIN across this far from the head, then widens
PIN_END = 4.98 - THINNER  # the shaft across at its widest, next to its end
PIN_TIP = 0.5  # the radius the shaft's end rounds over with, so it finds the hole

# The plug. Its shape is measured on a model of the holder, ikea130884 v2.stl, which is smaller than IKEA's part:
# the model's flange is 18 mm across and its collar 9.5 mm, and the user measured 20 mm and 10.55 mm on a holder on
# the desk. Both are 10/9, so every size of the model is made that much bigger.
RING = 20  # IKEA's flange across, the user's measurement on a holder on the desk
MODEL_FLANGE = 18  # the model's flange across
SCALE = RING / MODEL_FLANGE
SLIDE = 0.2  # the room round the pin where it slides, on each side
FLANGE = MODEL_FLANGE * SCALE  # the flange across, where it lies against the desk
RIM = 16 * SCALE  # the flange across at its rim, the edge away from the desk: its side slopes
FLANGE_THICK = 2 * SCALE  # the flange, from its rim to the desk
RECESS = 1 * SCALE  # the recess inside the rim, deep; the pin's head sits in it
RECESS_FLOOR = 14 * SCALE  # that recess across at its floor: it widens to RIM at the rim
COLLAR = 9.5 * SCALE  # the round shaft across, next to the flange
COLLAR_HEIGHT = 3 * SCALE  # that shaft, up from the flange
NECK = 8.8 * SCALE  # the shaft across between the collar and the first barb
NECK_HEIGHT = 1 * SCALE  # that neck, up from the collar
BARB = 10 * SCALE  # a barb across at its wide end, which faces the flange
BARB_ROOT = 7.6 * SCALE  # a barb across at its narrow end
BARB_PITCH = 1.2 * SCALE  # a barb, up
BARBS = 6
TIP = 7 * SCALE  # the prongs across at their end
TIP_HEIGHT = 1.5 * SCALE  # the last barb, which narrows to TIP
HOLE = 4 * SCALE  # the hole through the prongs: narrower than the pin, which pushes the prongs apart
ENTRY = PIN_END + 2 * SLIDE  # the hole through the flange and the collar, which do not give: the pin's wide end
# slides through it
HOLE_EDGE = (PIN - ENTRY) / 2 + PIN_ROOT + SLIDE  # the hole's edge in the recess is cut away this far, so it clears
# the pin's root
SLOT = 1 * SCALE  # each of the two slots that split the shaft into four prongs, wide
PIN_OUT = 2  # the pin is modelled out of the plug, its end this far under the rim: in the plug it spreads the prongs

RECESS_SLOPE = (RIM - RECESS_FLOOR) / 2 / RECESS  # how much the recess widens for every mm toward the rim
COLLAR_Z = FLANGE_THICK  # where the collar starts
NECK_Z = COLLAR_Z + COLLAR_HEIGHT  # where the neck starts, and the slots
BARB_Z = NECK_Z + NECK_HEIGHT  # where the first barb starts
TIP_Z = BARB_Z + BARBS * BARB_PITCH  # where the last barb starts
TOP = TIP_Z + TIP_HEIGHT  # the prongs' end
WIDENING = PIN_LENGTH - PIN_STRAIGHT - PIN_TIP  # the length the pin's shaft widens over
WIDE_Z = RECESS + PIN_STRAIGHT  # where the pin's shaft starts to widen
HEAD_Z = RECESS - HEAD_THICK  # the head's outer face, which is below the rim
VIEWS = (
    *plate.ANGLE,
    ("under.png", -30, -60, "From the side of the room: the pin under the plug's hole"),
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
    # The hole is ENTRY across up to where the slots start, then narrows at 45° to HOLE between the prongs.
    narrowing = (ENTRY - HOLE) / 2
    hole = Pos(0, 0, -CUT) * Cylinder(HOLE / 2, TOP + 2 * CUT, align=MIN)
    hole += Pos(0, 0, -CUT) * Cylinder(ENTRY / 2, NECK_Z + CUT, align=MIN)
    hole += Pos(0, 0, NECK_Z) * Cone(ENTRY / 2, HOLE / 2, narrowing, align=MIN)
    hole += Pos(0, 0, RECESS) * Cone(ENTRY / 2 + HOLE_EDGE, ENTRY / 2, HOLE_EDGE, align=MIN)
    return flange + shaft - recess - hole - slot() - Rot(0, 0, 90) * slot()


def head_profile():
    """Half the head from the side: x from its middle, and the sketch's y is up from its outer face."""
    edge = Rectangle(HEAD / 2, HEAD_EDGE, align=Align.MIN)
    middle = Rectangle(HEAD_FLAT / 2, HEAD_THICK, align=Align.MIN)
    # The side runs straight from the edge to this round, which ends in the flat face.
    corner = Pos(HEAD_FLAT / 2, HEAD_THICK - HEAD_ROUND) * Circle(HEAD_ROUND)
    return make_hull((edge + middle + corner).edges())


def root_profile():
    """Half the round between the shaft and the head from the side, the head's flat face at the sketch's y = 0."""
    corner = Pos(PIN / 2, 0) * Rectangle(PIN_ROOT, PIN_ROOT, align=Align.MIN)
    return corner - Pos(PIN / 2 + PIN_ROOT, PIN_ROOT) * Circle(PIN_ROOT)


def tip_profile():
    """Half the shaft's round end from the side, its widest at the sketch's y = 0."""
    flat = PIN_END / 2 - PIN_TIP  # the end's flat face, from the middle
    quarter = Pos(flat, 0) * Circle(PIN_TIP) & Pos(flat, 0) * Rectangle(PIN_TIP, PIN_TIP, align=Align.MIN)
    return Rectangle(flat, PIN_TIP, align=Align.MIN) + quarter


def pin():
    head = Pos(0, 0, HEAD_Z) * revolve(Plane.XZ * head_profile(), Axis.Z)
    # The shaft starts at the head's outer face, inside the head.
    shaft = Pos(0, 0, HEAD_Z) * Cylinder(PIN / 2, HEAD_THICK + PIN_STRAIGHT, align=MIN)
    root = Pos(0, 0, RECESS) * revolve(Plane.XZ * root_profile(), Axis.Z)
    wide = Pos(0, 0, WIDE_Z) * Cone(PIN / 2, PIN_END / 2, WIDENING, align=MIN)
    tip = Pos(0, 0, RECESS + PIN_LENGTH - PIN_TIP) * revolve(Plane.XZ * tip_profile(), Axis.Z)
    return head + shaft + root + wide + tip


def main():
    # The recess's floor hangs over the plate, so it prints on supports. They stand on the plate only: the barbs'
    # flat faces are 1.3 mm ledges and print without.
    supports = {"enable_support": "1", "support_on_build_plate_only": "1"}
    out = Pos(0, 0, -(RECESS + PIN_LENGTH + PIN_OUT)) * pin()
    plate.run(HERE, printed={"plug": plug(), "pin": out}, slicer={"plug": supports}, views=VIEWS)


if __name__ == "__main__":
    main()
