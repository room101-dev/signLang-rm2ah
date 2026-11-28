# Matrix change notes

Status: **no matrix values have been changed.** Test the current build first.

Current build under test:
- `make-gest3.py` — 26 letters, 8 values per pose, no pinky column.
- `gest-loop6.sh` — calls the driver via `python3`.
- `als-sign-array.md` — matrix 2 (with pinky) and matrix 3 (driver array).
- Reference: `als-std-fingering.md`.

## 1. Old array vs new

The old matrix in `old/als-sign-matrix.md` used neutral `0,0` placeholders:

- `B` fingers were `0,0,0,0,0,0` — not extended.
- `D`, `G`, `H`, `L`, `Z` index was `0,0` — not pointed or extended.
- `K`/`P` used `-30,-30` — both joints the same sign, not a real curl.
- `I`, `J`, `Y` were omitted.

The new matrix is anchored to demo poses (`-35,35` open, `90,-90` fist,
`-40,40` point, `55,-55` / `-10,-85` F, Victory and Spread values) with named
curl levels. All 26 letters are present. Matrix 3 is matrix 2 with `Pk1/Pk2`
removed, and it matches `make-gest3.py` exactly.

## 2. Problems in the current matrices

### Definite — contradict `als-std-fingering.md`

| Letter | Current | Problem |
| --- | --- | --- |
| O | fingers + pinky `27,-27` | Same light curl as C; O needs a closed ring to the thumb. |
| D | middle/ring/pinky `27,-27` | Too open for “curved to touch thumb tips”. |
| R | middle `-30,30` | Extended, not crossed over the index. |
| A | thumb `90,-90` | Full close, not “rests beside index”. |
| C | thumb `40,-40` | Same as B; C’s thumb must curve to meet the fingers. |
| Z note | “= G handshape” | Z thumb `75,-5`, G thumb `-30,30` — not equal. |

### Needs hardware check / calibration

| Letter | Value | Concern |
| --- | --- | --- |
| K / P | middle `-4,4`, thumb `0,0` | No anchor for “middle angled forward/up” or thumb between index/middle. |
| T | thumb `0,0` | “Tucked between index & middle” unverified. |
| U / V | thumb `90,-90` | A closed thumb does not “hold down ring & pinky”. |
| W | thumb `55,-55` | Interpolated; the demo spread pose uses thumb `-4,90`. |
| M / N | thumb `75,-5` | Across front vs “tucked under” the fingers. |
| G / Q | thumb `-30,30` | “Parallel to index, slightly below” unverified. |
| B | thumb `40,-40` | Plausible but interpolated. |
| E | fingers `59,-59` | May need a tighter curl for “fingertips near thumb”. |

## 3. Hardware limits — not tuple problems

- No pinky servo: matrix 3 `I`, `J`, `Y` are approximations; matrix 2 has the pinky columns.
- `J` and `Z` need motion; a static tuple cannot draw the hook or stroke.
- `K`/`P` and `G`/`Q` need wrist orientation to be distinguished; palm orientation is mostly absent.
- `MIDDLE_POS` is still the author’s placeholder; clamping fires on many letters.

## 4. Document issues

- `als-sign-array.md` contains chat/meta lines (1, 30–38, 77) and stale “Plan mode / display only” text.
- `README.md` names `als-sign-matrix.md`, which is now in `old/`; the current reference is `als-std-fingering.md`.
- `old/als-sign-matrix.md` is history only — do not use it as a source.

## 5. Test before changing anything

1. `python3 make-gest3.py --list -v` — confirm 26 letters and no errors.
2. `python3 make-gest3.py <letter> --dry -v` for all 26 letters.
3. On the laptop connected to the AH and Pi-4, form each letter and compare the physical hand
   against `als-std-fingering.md`: which fingers are extended/curved/curled, thumb position,
   palm orientation.
4. Record observed mismatches against section 2.
5. Only after testing, apply the fixes below and regenerate matrix 3 and `make-gest3.py` together.

## 6. Proposed fixes — deferred, do not apply yet

Definite:

| Letter | Change |
| --- | --- |
| O | fingers + pinky `27,-27` → `59,-59`; thumb stays `-10,-85` |
| D | middle/ring/pinky `27,-27` → `59,-59` |
| A | thumb `90,-90` → `-15,-15` |
| C | thumb `40,-40` → `55,-55` |
| Z note | remove “= G handshape” |

Candidates requiring hardware confirmation:

| Letter | Change |
| --- | --- |
| R | middle `-30,30` → `-30,60` (crossing swing; check direction) |
| U / V | thumb `90,-90` → `75,-5` |
| K / P | middle `-4,4` → `-35,35`, thumb `0,0` → `-15,-15` |
| T | thumb `0,0` → `-15,-15` |
