# home

Parts and pieces that make things nicer at home, 3D printed on a Bambu Lab P2S. Each part is a
Python script on build123d under `parts/`, built into a Bambu Studio project by `bin/part`.
`README.md` has the layout, the setup, every command, the slicer settings and the calibration; it
is kept current in the same change as the thing it describes, and so is `bin/part`'s header, which
`--help` prints.

## Commands

- `bin/part` lists the parts; `bin/part <name>` builds one into `build/` and checks it;
  `--pictures` also draws its committed pictures; `--all` builds every part; `--new <name>` starts
  one from `lib/template`; `--printer` and `--material` build for another entry in `printers.toml`;
  `--calibration` builds the calibration piece; `--test` runs the tests of what is in `lib/`.
- `bin/part <name> --open` opens the plate in Bambu Studio. It is the user's to run: the sandbox
  does not open apps. Slicing and sending to the printer happen there, by the user.
- `bin/part <name> --desktop` copies each printed piece's STL to the desktop. It is the user's to
  run too: the sandbox does not write there. `DESKTOP` names another directory.
- `uv sync --locked` makes the environment once per machine and needs the network, so it is the
  user's to run too. `bin/part` needs no network after it.

The `/calibrate` skill takes the user through calibrating a printer in a material: the piece built
and printed, its rows read one at a time, the codes written into `printers.toml`
(`.claude/skills/calibrate/`). The `/unslop` skill applies to everything written here.

## Working agreements

**The user decides what a part is.** What it holds, where it goes, which screws, magnets or other
bought parts it uses, and how it looks are the user's choices. Claude proposes, lays out what each
choice costs, and asks. A measurement of something in the house comes from the user; Claude does
not guess one, and asks for it when the model needs it.

**A part is done when it has printed and fits.** Claude's part ends at a build that passes and
pictures that show it. The user prints it and says what came out; each print is a commit, and
iterations stay in the part's directory.

**Committing is the user's call.** Ask.

## The model

- A part is one directory under `parts/`, with a `part.py`, a `README.md` and `pictures/`. What
  `bin/part` writes goes to `build/` and is never committed.
- Each printed piece is a function of its own, named for the piece: `bracket`, `cap`. A part
  bought rather than made is a placeholder: a block of its outline, handed to `plate.run` as
  `bought`, so the check finds a printed piece that runs into it. No vendor model is imported.
- Printed pieces are modelled where they sit when the thing is put together. How each lies on the
  plate is the `turn` handed to `plate.run`, and how many the plate holds its `copies`.
- Shapes are placed by coordinates worked out from the dimensions, never by picking a face or an
  edge of another shape. A face's index changes when an earlier feature does, and the model breaks
  without an error.
- What the parts share, in `lib/`, changes only in a way every part still builds with:
  `bin/part --all` passes after it, and `bin/part --test`.

## Numbers

- Every dimension is a named constant at the top of `part.py`, with a comment where the name does
  not say what it is. The shapes use those names and what is worked out from them, never a
  typed-in number. A dimension change is then one line, and the diff shows it.
- A dimension of something bought or measured says where it comes from in its comment: a
  standard, a datasheet, or the user's measurement and what it was measured on.
- A fit that depends on the printer and the material, a hole a screw slides through, a pocket a
  nut presses into, a hole that grips another printed piece, is read from `printers.toml` through
  `chosen().fits`, never typed in. A new kind of fit gets a letter and its clearances in
  `lib/printers.py`, a row on the piece in `lib/calibration.py`, and a code in every material of
  every printer. A piece that only has to slide into place, with 0.2 mm a side or more, needs no
  measured fit: its clearance is a named constant.

## The design

What a change to a part is checked against, beside the code. The printer is a Bambu Lab P2S with
a 0.4 mm nozzle and a 256 mm plate.

- **It prints.** Every printed piece fits the plate, lying the way the part's README says it
  prints. A wall is at least 1.2 mm, three lines of the nozzle; one that holds a screw or takes a
  load, at least 2 mm. A skin over a blind pocket that carries no load may be 0.6 mm, three
  layers, and its comment says so.
- **Its supports are checked.** A change to a printed piece is checked, with the piece turned the
  way it prints, for every overhang past 45° from upright and every bridge longer than 20 mm.
  Each one is designed out, or named in the part's README as a place that takes supports, with
  the setting for it in the part's `slicer`.
- **It carries its load the right way.** Layers split apart before they break across, so a hook,
  a clip or a tab that bends lies on the plate with its layers along the load, and the README
  says which way it prints and why.
- **It fits.** Every clearance between a printed piece and something else is a named constant or
  a fit from `printers.toml`: 0.2 mm a side or more where it slides, less only where it is meant
  to grip, and the comment says which.
- **It goes together.** Every piece can be put in and taken out in an order the part's README
  states, every screw can be reached with a driver in that order, and each one's size and length
  is in the README.

## The check

- `bin/part <name>` is the part's test: a part has no tests beside it. It passes before the part
  is committed. What is in `lib/` is code like any other, with tests in `lib/test_*.py`.
- A part's pictures are committed, and drawn again by `bin/part <name> --pictures` in every change
  that moves the model, so they always show the model beside them. Claude reads them after
  drawing them: a picture is how a wrong shape is seen before it is printed.
- A new part is listed in `README.md`, *Parts*.
- The Python versions are pinned exactly in `pyproject.toml` and locked in `uv.lock`, so every
  machine builds the same shapes.

## Git and the sandbox

Everything Claude runs goes through the Claude Code sandbox: `allowUnsandboxedCommands` is `false`
in `.claude/settings.json`, so anything not on `excludedCommands` runs sandboxed or fails.

- Commits are SSH-signed and need the key loaded in the agent, which the sandbox reaches because
  the settings allow all unix sockets. `Couldn't find key in agent?` means the key is not loaded:
  ask the user to run `ssh-add`, then retry. After a commit, check that it carries a `gpgsig`
  header (`git cat-file commit HEAD`); one without is a failure to stop on, not something to push.
- Only git's network verbs are excluded from the sandbox: `push`, `pull`, `fetch`, `clone`,
  `ls-remote`. An exclusion matches the whole command line, so these run bare: `git push origin
  main`, not `cd … && git push … | tail`.
- `bin/part --open` and `uv sync` are the user's to run: the sandbox does not open apps, and it
  does not reach the package index.
- A tool that fails on a sandbox denial gets the grant it asks for; it is never worked around.
  Name the denial and the grant it needs, and the user decides. A network grant, unix sockets
  among them, takes effect after a session restart.

## Words

Every word in a README, a comment or a script's header is plain and to the point. Present tense,
what the thing is and does. No "previously", no alternatives that are not built: git is the
history. Short sentences. A fact, then the next fact.
