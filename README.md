# home

Parts and pieces that make things nicer at home, 3D printed. Each one is a Python script on
[build123d](https://build123d.readthedocs.io), built into a Bambu Studio project by `bin/part`.

| | |
| --- | --- |
| `parts/` | One directory per part |
| `bin/part` | Builds a part into printable files and checks it |
| `printers.toml` | The Bambu Lab printers the parts are printed on, and for each material the fits its calibration piece showed |
| `lib/plate.py` | What every build does once its shapes are made: the check, the plate, the files and the pictures |
| `lib/bambu.py` | Writes the plate as a Bambu Studio project with each part's own settings (*Slicer settings*) |
| `lib/printers.py` | Reads `printers.toml` and what each code in it stands for |
| `lib/preview.py` | Draws pictures of a part with matplotlib |
| `lib/calibration.py` | The calibration piece, which shows what fits a printer makes in a material |
| `lib/template/` | What `bin/part --new` starts a part from |
| `lib/test_*.py` | Tests of what the parts share, run with `bin/part --test` |
| `pyproject.toml`, `uv.lock` | The Python versions every part is built with |

## Parts

A part is a directory under `parts/`, named for the thing, `hook`, `cable-clip`. It may print as
several pieces: one directory holds everything that goes together.

| File | What it holds |
| --- | --- |
| `part.py` | The model: its dimensions at the top, then one function per printed piece |
| `README.md` | What it is and where it goes, its pieces, how they print and go together |
| `pictures/` | Pictures of it, drawn by `bin/part <name> --pictures` and committed, so the repository shows the part without building it |

A part changes in place: iterations on it stay in its directory, however many prints they take,
and each print is a commit.

| Part | |
| --- | --- |
| [`bekant-net-hook`](parts/bekant-net-hook/) | A hook that gives the IKEA Bekant's cable net slack |
| [`drawer-glass-clip`](parts/drawer-glass-clip/) | A channel that connects a plate of glass to the front of a drawer |
| [`door-switch-clamp`](parts/door-switch-clamp/) | A clamp that holds the door switch for the light and covers its wires |

## Setup

Once per machine, install uv (`brew install uv`) and Python 3.12.16 with it
(`uv python install 3.12.16`), then make the environment from the lock file:

```sh
uv sync --locked
```

`bin/part` runs in it from then on, without the network. Opening a plate needs
[Bambu Studio](https://bambulab.com/en/download/studio).

## Building one

```sh
bin/part                   # the parts
bin/part --new hook        # start parts/hook from lib/template
bin/part hook              # parts/hook: the printable files, and the check
bin/part hook --pictures   # and its pictures, which are committed
bin/part hook --open       # then open the plate in Bambu Studio
bin/part hook --desktop    # then copy each printed piece's STL to the desktop
bin/part --all             # build and check every part
bin/part hook --printer p2s --material petg   # for a printer and material in printers.toml
bin/part --calibration     # the calibration piece
bin/part --test            # the tests of what the parts share
```

A build is for one printer and one material, `printers.toml`'s defaults unless `--printer` and
`--material` name others; the committed pictures are drawn for the defaults. It writes to
`build/<part>/<printer>-<material>/`, which is not committed:

| File | What it is |
| --- | --- |
| `plate.3mf` | Every printed piece on the printer's plate, each turned the way it prints and as many times as it is needed, as a Bambu Studio project |
| `*.stl` | Each printed piece on its own, turned the same way |
| `<part>.step` | The whole thing put together, with the bought parts as blocks. Open it in a CAD viewer to turn it round |

The build stops when a printed piece is not one solid, when two pieces overlap, a printed one
and another or a printed one and a bought one, when `printers.toml` has not got the printer or
the material asked for, or when the pieces do not fit the printer's plate.

From there to the printer: `--open` opens `plate.3mf` in Bambu Studio, with the presets the
material's comment in `printers.toml` names selected there. Slice it, and send it to the printer.

## Slicer settings

An export carries only what a single piece changes, such as supports or a brim; it is the
`slicer` a part's `part.py` hands to `plate.run`, by Bambu Studio's names. Everything else, the
process, the printer and the filament, Bambu Studio takes from the presets selected when the
plate is opened: the ones the material's comment in `printers.toml` names, which the calibration
piece printed with, so the fits read off it hold. Changing the preset, or the layer height, line
widths, wall order, outer wall speed, flow or X-Y compensation in it, changes the fits, so the
material is calibrated again after it.

Bambu Studio reads a piece's own settings from the project's layout as it wrote it in version
2.09.01 (`lib/bambu.py`). It is not documented: after a Bambu Studio update, open an export and
check that the per-piece settings are still there.

## Calibration

How tight a hole comes out depends on the printer and on the material, so the fits the parts
depend on are measured on each, once, with a calibration piece, and kept in `printers.toml`. The
piece is a 62 × 42 × 4 mm plate with three rows, one fit each, made five times from tight to
loose. A loose 6 mm peg prints beside it. Every feature has a code engraved under it, its row's
letter and its column's number, and `printers.toml` holds the code of the one that fits:

| Codes | Fit in `printers.toml` | Tried with | The first one, from 1, where |
| --- | --- | --- | --- |
| S1–S5, small round holes | `screw_hole` | An M3 screw | it slides through without force |
| N1–N5, hex pockets, from below | `nut_pocket` | An M3 nut | it presses in by thumb and does not turn |
| P1–P5, round holes at the bottom | `printed_grip` | The loose peg | it pushes in firmly and holds |

A part reads a fit as a clearance a side, in mm, and adds it to the size of whatever goes in the
hole: `FITS.screw_hole` round any screw that slides through, `FITS.nut_pocket` round anything
pressed in, `FITS.printed_grip` where one printed piece holds another.

`lib/printers.py` holds what clearance each code stands for; `bin/part --calibration` prints them.
A code keeps its meaning for good, since `printers.toml` may hold it for any printer: a row that
needs a looser fit gets columns added at its end, and one that needs a tighter fit gets a new
letter. A column is never shifted.

For a new printer, or a new material on one, the `/calibrate` skill in Claude Code walks through
these steps and writes the file:

1. A new material gets its table in `printers.toml` first, with `calibrated = false` and a comment
   naming the Bambu Studio presets it prints with (*Slicer settings*), and a new printer its own
   `[printers.<name>]` table, with its model, plate and nozzle.
   `bin/part --calibration --printer <printer> --material <material>` builds
   `build/calibration/<printer>-<material>/calibration.3mf`, and `--open` opens it in Bambu
   Studio. Print it top face up with those presets, on the printer.
2. Try each row with its part, from 1, and note the code under the first one that fits.
3. In `printers.toml`, under `[printers.<printer>.materials.<material>]`, set each fit to its code,
   such as `nut_pocket = "N2"`, and `calibrated = true`.
4. `bin/part <name> --printer <printer> --material <material> --open` builds a part with those
   fits and opens it in Bambu Studio.

A row where nothing fits, or where the first already fits loosely, is out of range: add columns or
a letter in `lib/printers.py`'s `CODES`, as above, and print a new piece.

The P2S's PLA codes were read off the calibration piece of `../bliep`, whose S, N and P rows are
the same features as this one's.
