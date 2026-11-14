"""Pictures of a part, drawn with matplotlib, for a look without a CAD viewer."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

LIGHT = np.array([0.4, -0.5, 0.8]) / np.linalg.norm([0.4, -0.5, 0.8])


def _mesh(shape, tolerance):
    verts, tris = shape.tessellate(tolerance, 0.3)
    if not tris:
        return np.empty((0, 3, 3))
    v = np.array([(p.X, p.Y, p.Z) for p in verts])
    return _in_order(v[np.array(tris)])


def _in_order(t):
    """Triangles in an order of their own, by where they are. OpenCascade may hand the same shape's faces over in
    another order from one run to the next, and a triangle starting from another corner, and matplotlib draws
    triangles at the same depth in the order given, so the same model would draw different pictures. Each triangle
    starts from its least corner, by x, then y, then z, its winding kept, and then the triangles are sorted. They are
    rounded to 0.1 µm first, -0 made 0, and a triangle with two corners at the same place is dropped: it draws nothing,
    and which of the two it started from would depend on the order given."""
    t = np.round(t, 4) + 0.0  # adding 0 turns -0, which the same model may give in one run and not the next, into 0
    t = t[(t[:, 0] != t[:, 1]).any(1) & (t[:, 1] != t[:, 2]).any(1) & (t[:, 2] != t[:, 0]).any(1)]
    corners = t.reshape(-1, 3)
    order = np.lexsort(corners.T[::-1])
    rank = np.empty(len(order), dtype=int)
    rank[order] = np.arange(len(order))
    least = rank.reshape(len(t), 3).argmin(1)
    t = t[np.arange(len(t))[:, None], (least[:, None] + np.arange(3)) % 3]
    return t[np.lexsort(t.reshape(len(t), -1).T[::-1])]


def render(path, items, elev, azim, title, tolerance=0.2, size=(8, 8)):
    """items: (shape, rgb, alpha). Writes a PNG at path."""
    fig = plt.figure(figsize=size, dpi=110)
    ax = fig.add_subplot(projection="3d")
    # One collection, so matplotlib orders every triangle by depth, not each part as a whole.
    tris, faces = [], []
    for shape, rgb, alpha in items:
        t = _mesh(shape, tolerance)
        if len(t) == 0:  # a part the section cut takes away whole
            continue
        n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        shade = 0.45 + 0.55 * np.abs(n @ LIGHT)
        tris.append(t)
        faces.append(np.c_[np.clip(np.outer(shade, rgb), 0, 1), np.full(len(t), alpha)])
    t = np.concatenate(tris)
    ax.add_collection3d(Poly3DCollection(t, facecolors=np.concatenate(faces), linewidths=0))
    lo, hi = t.reshape(-1, 3).min(0), t.reshape(-1, 3).max(0)
    mid, half = (lo + hi) / 2, (hi - lo).max() / 2
    ax.set_xlim(mid[0] - half, mid[0] + half)
    ax.set_ylim(mid[1] - half, mid[1] + half)
    ax.set_zlim(mid[2] - half, mid[2] + half)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_title(title)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
