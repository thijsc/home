"""plate.py: the check, and the parts set out on the plate.

Run with `bin/part --test`.
"""

import contextlib
import io
import unittest

from build123d import Box, Pos, Rot

import plate


def quiet(f, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        return f(*args)


class Check(unittest.TestCase):
    def test_parts_that_touch_do_not_clash(self):
        printed = {"a": Box(10, 10, 10), "b": Pos(10, 0, 0) * Box(10, 10, 10)}
        self.assertEqual(quiet(plate.check, printed, {}), [])

    def test_two_printed_parts_that_overlap_clash(self):
        printed = {"a": Box(10, 10, 10), "b": Pos(9, 0, 0) * Box(10, 10, 10)}
        (a, b, v), = quiet(plate.check, printed, {})
        self.assertEqual((a, b), ("a", "b"))
        self.assertAlmostEqual(v, 100)

    def test_a_printed_part_and_a_bought_one_that_overlap_clash(self):
        found = quiet(plate.check, {"a": Box(10, 10, 10)}, {"screw": Pos(0, 0, 5) * Box(2, 2, 10)})
        self.assertEqual([(a, b) for a, b, _ in found], [("a", "screw")])

    def test_a_part_in_two_pieces_stops(self):
        with self.assertRaisesRegex(SystemExit, "a is not one valid solid"):
            quiet(plate.check, {"a": Box(5, 5, 5) + Pos(20, 0, 0) * Box(5, 5, 5)}, {})


class LayOut(unittest.TestCase):
    def boxes(self, placed):
        return {label: shape.bounding_box() for label, (_, shape) in placed.items()}

    def test_every_part_lies_on_the_bed_inside_the_plate(self):
        printed = {"a": Pos(5, 5, 5) * Box(40, 30, 10), "b": Pos(0, 0, -50) * Box(20, 20, 20)}
        for bb in self.boxes(plate.lay_out(printed, {}, {}, 256)).values():
            self.assertAlmostEqual(bb.min.Z, 0)
            self.assertGreaterEqual(bb.min.X, 0)
            self.assertLessEqual(bb.max.X, 256)
            self.assertLessEqual(bb.max.Y, 256)

    def test_a_part_is_turned_the_way_it_prints(self):
        placed = plate.lay_out({"a": Box(10, 20, 30)}, {"a": Rot(90, 0, 0)}, {}, 256)
        size = placed["a"][1].bounding_box().size
        self.assertAlmostEqual(size.Y, 30)
        self.assertAlmostEqual(size.Z, 20)

    def test_copies_are_numbered_and_keep_their_parts_name(self):
        placed = plate.lay_out({"hook": Box(10, 10, 10), "rail": Box(50, 10, 10)}, {}, {"hook": 3}, 256)
        self.assertEqual(sorted(placed), ["hook_1", "hook_2", "hook_3", "rail"])
        self.assertEqual(placed["hook_2"][0], "hook")

    def test_parts_do_not_touch_and_take_another_row_when_one_is_full(self):
        placed = plate.lay_out({"a": Box(100, 20, 5)}, {}, {"a": 5}, 256)
        boxes = list(self.boxes(placed).values())
        self.assertEqual(len({round(bb.min.Y, 3) for bb in boxes}), 3)
        for i, a in enumerate(boxes):
            for b in boxes[i + 1:]:
                apart = max(b.min.X - a.max.X, a.min.X - b.max.X, b.min.Y - a.max.Y, a.min.Y - b.max.Y)
                self.assertGreaterEqual(apart, plate.GAP - 1e-6)

    def test_parts_that_do_not_fit_the_plate_stop(self):
        with self.assertRaisesRegex(SystemExit, "more than the 180 mm plate"):
            plate.lay_out({"a": Box(100, 100, 5)}, {}, {"a": 4}, 180)
        with self.assertRaisesRegex(SystemExit, "more than the 180 mm plate"):
            plate.lay_out({"a": Box(200, 10, 5)}, {}, {}, 180)

    def test_the_same_parts_land_in_the_same_places(self):
        printed = {"a": Box(30, 30, 5), "b": Box(20, 30, 5), "c": Box(10, 40, 5)}
        first, again = (self.boxes(plate.lay_out(printed, {}, {}, 256)) for _ in range(2))
        self.assertEqual({k: (v.min.X, v.min.Y) for k, v in first.items()}, {k: (v.min.X, v.min.Y) for k, v in again.items()})


if __name__ == "__main__":
    unittest.main()
