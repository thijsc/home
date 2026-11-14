# bekant-net-hook

A hook that gives the IKEA Bekant's cable net slack. The net's loops are too tight on the net
holders under the desk. The hook's eye goes on a holder's shaft, under the holder's ring, and the
net's loop hooks into the other end, 40 mm further out.

![bekant-net-hook](pictures/angle.png)

![From the side](pictures/side.png)

## Parts

| Printed | Count | Prints | Supports |
| --- | --- | --- | --- |
| `hook` | 1 | Flat face down, pocket and hook up | Under the hook's top half and its lip |

The eye's hole is the holder's 10.55 mm shaft with 0.2 mm a side. The pocket round it is the
holder's 20 mm ring with 0.2 mm a side, and its floor is 1.55 mm thick, the room under the ring.
The rest is 4 mm thick.

The hook stands on the end of the arm and opens toward the shaft. Its back is straight, in line
with the arm's end, and rounds over at the top. Its top runs
6 mm further toward the shaft as a flat lip, which keeps the loop under it. The room inside is a
slot 4 mm high with a flat back. The wall over it is 3 mm and the wall behind it, at the arm's end,
6 mm. The hook is as wide as the arm, 12 mm.

The hook's top half and its lip hang over the arm and print on supports, which the plate turns on
for this piece (`enable_support`). The net pulls the hook along its layers, across the 6 mm wall where it
stands on the arm.

## Putting it together

1. Take the net holder off the desk.
2. Put the holder's shaft through the eye, the ring in the pocket.
3. Put the holder back, with the arm pointing at the net.
4. Slide the net's loop along the arm and under the hook.

## Printing

```sh
bin/part bekant-net-hook --open
```

![The plate](pictures/plate.png)
