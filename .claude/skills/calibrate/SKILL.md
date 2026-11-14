---
name: calibrate
description: Take the user through calibrating a Bambu Lab printer in one material for the printed parts. Builds the calibration piece with `bin/part --calibration`, tells the user how to print it, then walks them through its three rows one at a time, asking which engraved code fits, and writes the codes into printers.toml. Use when the user wants to calibrate a printer, a new material or filament (PETG, PLA, another), set up a new printer, or says a part's holes, nuts or fits come out too tight or too loose.
---

# Calibrate

The fits the parts depend on, a hole a screw slides through, a pocket a nut presses into, a hole that grips another printed part, change with the printer and the material. `README.md`, *Calibration*, is how they are measured; this skill walks the user through it. The user does the printing and the trying by hand, so the steps are theirs and the questions are short: one row at a time, the user's hands are busy with parts.

Copy this checklist and check it off:

```
- [ ] 1. Which printer and material
- [ ] 2. Build the piece
- [ ] 3. Print it
- [ ] 4. Read the three rows
- [ ] 5. Write printers.toml
- [ ] 6. Build the parts for it
- [ ] 7. Report
```

## 1. Which printer and material

Read `printers.toml`. Ask which printer and which material, with the ones it lists as options. A printer it does not list gets its own `[printers.<name>]` table now: ask for its Bambu Lab model; its plate and nozzle are that model's, and the user confirms them. The name is short and lower case, `p2s`, `a1-mini`.

If the material is already there with `calibrated = true`, say so and ask whether to measure it again, for a new spool, a new nozzle, changed presets or fits that came out wrong.

The piece prints with the Bambu Studio presets the parts print with, which the comment over the material's table in `printers.toml` names (`README.md`, *Slicer settings*). A new material gets its table now, before the piece is built: ask which process and filament presets the user prints it with, and write them in that comment, with `calibrated = false` and nothing else until step 5.

## 2. Build the piece

```sh
bin/part --calibration --printer <printer> --material <material>
```

It writes `build/calibration/<printer>-<material>/calibration.3mf`, a Bambu Studio project, and prints every code with its clearance. The codes are the same for every printer and material; only which one fits changes.

## 3. Print it

Tell the user, in these words or close to them:

- Open it in Bambu Studio with `bin/part --calibration --printer <printer> --material <material> --open`, theirs to run: the sandbox does not open apps.
- Print it engraved face up, in the material, with the presets `printers.toml` names for it, the ones the parts print with, and nothing changed in them: no supports, no brim, the hole and size compensation as the presets have them.
- The plate holds the piece and a loose peg beside it; both print.
- Have ready: an M3 screw, an M3 nut, and the peg once it is printed.

Then wait. The user comes back when the print is done.

## 4. Read the three rows

One question per row, in this order, each with the row's five codes as options. Every question says what to try, how, and what counts as fitting, because the user reads it with a part in hand. Try from 1, the tightest, and stop at the first that fits:

| Row | Part | How | Fits when |
| --- | --- | --- | --- |
| S1–S5, small round holes | An M3 screw | Push it through by hand, without turning it | It slides all the way through without force |
| N1–N5, hex pockets, on the underside | An M3 nut | Turn the piece over and press it in flat with a thumb | It goes in flush and does not turn when twisted with a screwdriver tip |
| P1–P5, round holes at the bottom | The loose peg printed beside the piece | Push it in by hand | It goes in firmly and holds, without a tool |

If nothing in a row fits, or the first one already fits loosely, the row is out of range: note which way, and after the three rows change `lib/printers.py`, then go back to step 2 for a new piece. A code keeps its meaning for good, since `printers.toml` may hold it for another printer or material: a row that needs looser fits gets columns added at the end of its letter's tuple in `CODES`, as a tuple of its own if other letters share it, and one that needs tighter fits gets a new letter in `CODES` with its own tuple, and `ROWS` moves that fit's row to it. Never take a letter out of `CODES`, and never shift or change a column that exists. Do not guess a code.

If a fit sits between two codes, the tighter one that still fits is the answer; a nut that needs a firm press is right, one that needs a tool is too tight.

## 5. Write printers.toml

Under `[printers.<printer>.materials.<material>]`, write the three codes and `calibrated = true`, keeping the comment on each line. A new material gets the table whole, in the same order as the others. Show the user the table as written.

## 6. Build the parts for it

```sh
bin/part --all --printer <printer> --material <material>
```

It reads the codes, builds every part with those fits and checks it. It stops on a code it cannot read, which means a typo in step 5. Then tell the user `bin/part <name> --printer <printer> --material <material> --open` opens one in Bambu Studio, theirs to run.

If the printer and material are the defaults in `printers.toml`, the fits the committed pictures show have changed: `bin/part <name> --pictures` draws a part's again.

## 7. Report

The printer and material, the three codes with the clearance each stands for, and which changed from before. Committing is the user's call; ask.
