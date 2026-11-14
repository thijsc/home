"""preview.py: the triangles it draws, and that the same shape draws the same picture.

Run with `bin/part --test`.
"""

import tempfile
import unittest
from pathlib import Path

import numpy as np
from build123d import Box, Compound, Cylinder, Pos

import preview


class Mesh(unittest.TestCase):
    def test_triangles_come_in_order_of_where_they_are(self):
        t = preview._mesh(Box(10, 20, 30) - Pos(0, 0, 10) * Cylinder(3, 20), 0.2)
        key = np.round(t.reshape(len(t), -1), 4)
        order = np.lexsort(key.T[::-1])
        self.assertTrue((order == np.arange(len(t))).all())

    def test_the_same_shape_built_in_another_order_meshes_the_same(self):
        a = preview._mesh(Box(10, 10, 10) + Pos(5, 0, 0) * Cylinder(3, 12), 0.2)
        b = preview._mesh(Pos(5, 0, 0) * Cylinder(3, 12) + Box(10, 10, 10), 0.2)
        self.assertEqual(a.shape, b.shape)
        np.testing.assert_allclose(a, b, atol=1e-4)

    def test_triangles_starting_from_other_corners_and_in_another_order_come_out_the_same(self):
        t = preview._mesh(Box(10, 20, 30) - Pos(0, 0, 10) * Cylinder(3, 20), 0.2)
        rng = np.random.default_rng(0)
        turned = np.stack([np.roll(x, k, 0) for x, k in zip(t, rng.integers(0, 3, len(t)))])[rng.permutation(len(t))]
        np.testing.assert_array_equal(preview._in_order(turned), t)

    def test_a_triangle_keeps_its_winding(self):
        t = np.array([[[1.0, 0, 0], [0, 1, 0], [0, 0, 0]]])
        np.testing.assert_array_equal(preview._in_order(t), [[[0, 0, 0], [1, 0, 0], [0, 1, 0]]])

    def test_a_triangle_with_two_corners_at_one_place_is_dropped(self):
        t = np.array([[[0.0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0.0, 0, 0], [1, 1, 0], [0.00001, 0, 0]]])
        np.testing.assert_array_equal(preview._in_order(t), t[:1])

    def test_minus_zero_comes_out_as_zero(self):
        t = np.array([[[-0.0, 0, 0], [1, 0, 0], [0, 1, -0.0]]])
        self.assertFalse(np.signbit(preview._in_order(t)).any())

    def test_a_shape_with_nothing_left_has_no_triangles(self):
        self.assertEqual(preview._mesh(Compound([]), 0.2).shape, (0, 3, 3))


class Render(unittest.TestCase):
    def test_the_same_shape_draws_the_same_picture(self):
        shape = Box(10, 20, 5) - Cylinder(3, 10)
        with tempfile.TemporaryDirectory() as d:
            paths = [Path(d) / f"{i}.png" for i in range(2)]
            for p in paths:
                preview.render(p, [(shape, (0.9, 0.7, 0.8), 1), (Compound([]), (0, 0, 0), 1)], elev=30, azim=-60, title="t")
            self.assertGreater(paths[0].stat().st_size, 0)
            self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())


if __name__ == "__main__":
    unittest.main()
