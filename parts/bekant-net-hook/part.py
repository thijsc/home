"""bekant-net-hook: a hook that moves a loop of the IKEA Bekant's cable net away from the desk's net holder.

The net's loops are too tight on the holders under the desk. The hook's eye goes on a holder's shaft, under the
holder's ring, and the hook that stands on its other end takes the net's loop REACH further out.

Every size is a named constant below. Coordinates: x from the shaft to the hook, y across, z up from the face that
lies on the plate.

Run through bin/part, which checks it and writes the printable files to build/.
"""

import sys
from pathlib import Path

from build123d import Align, Box, Cylinder, Pos, Rot

# What the parts share is in lib/; put it on the path, since bin/part's PYTHONPATH is not there when this file is
# run some other way.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import plate  # noqa: E402

HERE = Path(__file__).parent
CUT = 1  # a cut runs this far past what it cuts through, so it leaves no skin
MIN = (Align.CENTER, Align.CENTER, Align.MIN)
FROM_X = (Align.MIN, Align.CENTER, Align.MIN)

SHAFT = 10.55  # the shaft of the Bekant's net holder, the user's measurement on the desk
RING = 20  # the ring on top of that shaft, the user's measurement on the desk
SLIDE = 0.2  # a side, round the shaft and round the ring: they slide in
FLOOR = 1.55  # the hook under the holder's ring, the user's measurement of the room there
THICK = 4  # the hook everywhere else
RIM = 4  # the wall round the ring
REACH = 50  # from the middle of the shaft to where the loop's cord rests
WIDTH = 12  # the arm and the hook, across
SPACE = 4  # the room inside the hook, across, for the net's loop
HOOK_WALL = 3  # the hook's wall, round that room
LIP = 6  # the hook's top, past the half circle toward the shaft, which keeps the loop under it

POCKET = RING / 2 + SLIDE  # the radius of the pocket the ring sits in
HOOK_X = REACH - SPACE / 2  # the middle of the hook's round back, along the arm
END = REACH + HOOK_WALL  # the arm's end, which is the hook's back
HOOK_Z = THICK + SPACE / 2  # and up: the room inside the hook starts on the arm's top
VIEWS = (*plate.ANGLE, ("side.png", 0, -90, "From the side: the hook opens toward the shaft"))


def hook():
    eye = Cylinder(POCKET + RIM, THICK, align=MIN)
    arm = Box(END, WIDTH, THICK, align=FROM_X)
    pocket = Pos(0, 0, FLOOR) * Cylinder(POCKET, THICK, align=MIN)
    hole = Pos(0, 0, -CUT) * Cylinder(SHAFT / 2 + SLIDE, THICK + 2 * CUT, align=MIN)
    # The hook is the far half of a cylinder that stands on the arm, its axis across, with a lip toward the shaft.
    # Below the cylinder's middle its back is straight, in line with the arm's end.
    # The room inside is a slot with a flat back, open toward the shaft.
    outer = SPACE / 2 + HOOK_WALL
    half = Pos(0, 0, -WIDTH / 2) * Box(outer, 2 * outer, WIDTH, align=(Align.MIN, Align.CENTER, Align.MIN))
    curl = Pos(HOOK_X, 0, HOOK_Z) * Rot(90, 0, 0) * (Cylinder(outer, WIDTH) & half)
    back = Pos(HOOK_X, 0, THICK) * Box(outer, WIDTH, HOOK_Z - THICK, align=FROM_X)
    lip = Pos(HOOK_X - LIP, 0, HOOK_Z + SPACE / 2) * Box(LIP, WIDTH, HOOK_WALL, align=FROM_X)
    room = Pos(HOOK_X - LIP - CUT, 0, THICK) * Box(REACH - HOOK_X + LIP + CUT, WIDTH + 2 * CUT, SPACE, align=FROM_X)
    return eye + arm + (curl + back + lip - room) - pocket - hole


def main():
    # The hook's top half and its lip hang over the arm, so they print on supports.
    plate.run(HERE, printed={"hook": hook()}, slicer={"hook": {"enable_support": "1"}}, views=VIEWS)


if __name__ == "__main__":
    main()
