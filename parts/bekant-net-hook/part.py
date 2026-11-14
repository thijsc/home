"""bekant-net-hook: a hook that moves a loop of the IKEA Bekant's cable net away from the desk's net holder.

The net's loops are too tight on the holders under the desk. The hook's eye goes on a holder's shaft, under the
holder's ring, and the hook that stands on its other end takes the net's loop REACH further out.

Every size is a named constant below. Coordinates: x from the shaft to the hook, y across, z up from the face that
lies on the plate.

Run through bin/part, which checks it and writes the printable files to build/.
"""

import sys
from pathlib import Path

from build123d import Align, Circle, Cylinder, Pos, Rectangle, Rot, extrude, make_hull

# What the parts share is in lib/; put it on the path, since bin/part's PYTHONPATH is not there when this file is
# run some other way.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import plate  # noqa: E402

HERE = Path(__file__).parent
CUT = 1  # a cut runs this far past what it cuts through, so it leaves no skin
MIN = (Align.CENTER, Align.CENTER, Align.MIN)

SHAFT = 10.55  # the shaft of the Bekant's net holder, the user's measurement on the desk
RING = 20  # the ring on top of that shaft, the user's measurement on the desk
SLIDE = 0.2  # a side, round the shaft and round the ring: they slide in
FLOOR = 1.55  # the hook under the holder's ring, the user's measurement of the room there
THICK = 6  # the eye and the arm, up from the plate
RIM = 4  # the wall round the ring
REACH = 32  # from the middle of the shaft to where the loop's cord rests
WIDTH = 14  # the arm and the hook, across
SPACE = 6  # the room inside the hook at its back, up from the arm, for the net's loop
MOUTH = 4  # the room under the hook's tip, up from the arm, which the loop passes on its way in
HOOK_WALL = 4  # the hook's wall over that room, at its back
BACK_WALL = 2 * HOOK_WALL  # the hook's wall behind that room, at the arm's end
LIP = 6  # from the middle of the room's round back to the middle of the tip, along the arm

POCKET = RING / 2 + SLIDE  # the radius of the pocket the ring sits in
EYE = POCKET + RIM  # the radius of the eye
END = REACH + BACK_WALL  # the arm's end, which is the hook's back
ROUND = SPACE / 2 + HOOK_WALL  # the radius the hook's back rounds over with, at the top
ROUND_X = END - ROUND  # the middle of that round, along the arm
ROOM_X = REACH - SPACE / 2  # the middle of the room's round back, along the arm
LIP_X = ROOM_X - LIP  # the middle of the tip, along the arm
HOOK_Z = THICK + SPACE / 2  # the middle of both rounds, up: the room inside the hook starts on the arm's top
TOP = THICK + SPACE + HOOK_WALL  # the hook's top
TIP = (TOP - THICK - MOUTH) / 2  # the radius of the tip, which comes down from the top to the mouth
VIEWS = (*plate.ANGLE, ("side.png", 0, -90, "From the side: the hook opens toward the shaft"))


def box(x_from, x_to, z_from, z_to):
    """A rectangle of the side profile, from its corners."""
    return Pos(x_from, z_from) * Rectangle(x_to - x_from, z_to - z_from, align=Align.MIN)


def profile():
    """The arm and the hook from the side: x along the arm, and the sketch's y is the part's z."""
    arm = box(0, END, 0, THICK)
    # The hook stands on the arm: a back that is straight below the room's middle and rounds over above it, a top
    # that runs toward the shaft, and a round tip that comes down from the top to the mouth.
    curl = Pos(ROUND_X, HOOK_Z) * Circle(ROUND) & box(ROUND_X, END, HOOK_Z, TOP)
    back = box(ROUND_X, END, THICK, HOOK_Z)
    top = box(LIP_X, ROUND_X, THICK, TOP)
    tip = Pos(LIP_X, TOP - TIP) * Circle(TIP)
    # The room inside is round at its back and narrows to the mouth: its ceiling comes down in a straight line
    # from the round back to the tip, so the inside has no corner.
    ends = Pos(ROOM_X, HOOK_Z) * Circle(SPACE / 2) + Pos(LIP_X, THICK + MOUTH / 2) * Circle(MOUTH / 2)
    room = make_hull(ends.edges())
    return arm + (curl + back + top + tip - room)


def hook():
    eye = Cylinder(EYE, THICK, align=MIN)
    pocket = Pos(0, 0, FLOOR) * Cylinder(POCKET, THICK, align=MIN)
    hole = Pos(0, 0, -CUT) * Cylinder(SHAFT / 2 + SLIDE, THICK + 2 * CUT, align=MIN)
    side = Rot(90, 0, 0) * extrude(profile(), WIDTH / 2, both=True)
    return eye + side - pocket - hole


def main():
    # The hook's top and its tip hang over the arm, so they print on supports.
    plate.run(HERE, printed={"hook": hook()}, slicer={"hook": {"enable_support": "1"}}, views=VIEWS)


if __name__ == "__main__":
    main()
