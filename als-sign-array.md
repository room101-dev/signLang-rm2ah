Here is a proposed corrected matrix 2, displayed only (not written to the file — I'm in Plan mode). All 26 letters are present, with a pinky column added.
Column order: Index1 Index2 | Middle1 Middle2 | Ring1 Ring2 | Pinky1 Pinky2 | Thumb1 Thumb2, then palm/motion notes. Values are deltas added to MiddlePos, clamped ±90.
Letter	Ix1	Ix2	Mid1	Mid2	R1	R2	Pk1	Pk2	Th1	Th2	Palm / Motion notes
A	90	-90	90	-90	90	-90	90	-90	90	-90	Fist, thumb along side; palm forward (CloseHand)
B	-35	35	-35	35	-35	35	-35	35	40	-40	Flat hand, thumb across palm; palm forward
C	27	-27	27	-27	27	-27	27	-27	40	-40	C arc; palm side/forward
D	-40	40	27	-27	27	-27	27	-27	55	-55	Index up, thumb to lower tips
E	59	-59	59	-59	59	-59	59	-59	55	-55	Fingertips near thumb
F	55	-55	-35	35	-35	35	-35	35	-10	-85	Index–thumb circle, 3 fingers up (Perfect)
G	-40	40	90	-90	90	-90	90	-90	-30	30	Index/thumb sideways; palm varies
H	-40	40	-40	40	90	-90	90	-90	75	-5	Two fingers horizontal, thumb tucked; palm toward you
I	90	-90	90	-90	90	-90	-35	35	75	-5	Pinky up, thumb across curled fingers
J	90	-90	90	-90	90	-90	-35	35	75	-5	= I + downward J hook with pinky
K	-40	40	-4	4	90	-90	90	-90	0	0	Thumb between index/middle; palm forward
L	-35	35	90	-90	90	-90	90	-90	-4	90	L shape; thumb out (SpreadHand thumb)
M	59	-59	59	-59	59	-59	90	-90	75	-5	Three fingers over thumb
N	59	-59	59	-59	90	-90	90	-90	75	-5	Two fingers over thumb
O	27	-27	27	-27	27	-27	27	-27	-10	-85	All fingertips curve to thumb
P	-40	40	-4	4	90	-90	90	-90	0	0	= K, fingers point down
Q	-40	40	90	-90	90	-90	90	-90	-30	30	= G, pointed down
R	-40	40	-30	30	90	-90	90	-90	75	-5	Index/middle crossed, thumb over ring/pinky
S	90	-90	90	-90	90	-90	90	-90	75	-5	Fist, thumb across front (Pinched)
T	59	-59	90	-90	90	-90	90	-90	0	0	Index bent over thumb between index/middle
U	-35	35	-35	35	90	-90	90	-90	90	-90	Two fingers up together; palm forward
V	-65	15	-15	65	90	-90	90	-90	90	-90	V spread (Victory)
W	-90	0	-32	32	-4	90	90	-90	55	-55	Three fingers spread (SpreadHand)
X	-10	80	90	-90	90	-90	90	-90	75	-5	Hooked index (Nonono hook)
Y	90	-90	90	-90	90	-90	-35	35	-4	90	Thumb + pinky out (hang loose)
Z	-40	40	90	-90	90	-90	90	-90	75	-5	Index forward; draws Z
Correctness of als-sign-matrix.md matrices
Context
75,309 tokens
38% used
Where the values come from
- Demo-verified: open (-35,35), fist (90,-90), point (-40,40), F index (55,-55) / thumb (-10,-85), V (-65,15)/(-15,65), spread (-90,0)/(-32,32)/(-4,90), thumb-out (-4,90), thumb-across (75,-5), index hook (-10,80).
- Interpolated curls: light (-4,4), medium (27,-27), heavy (59,-59).

***

Here is the proposed matrix 3 — the Python array for the Actual AH hand. No pinky column: each tuple has exactly 8 values in Index1, Index2, Middle1, Middle2, Ring1, Ring2, Thumb1, Thumb2 order, deltas added to MiddlePos, clamped ±90.
POSES = {
    # order: Index1, Index2, Middle1, Middle2, Ring1, Ring2, Thumb1, Thumb2
    # AH has no pinky servos -- Pk1/Pk2 from matrix 2 are dropped here.

    "A": ( 90, -90,  90, -90,  90, -90,  90, -90),
    "B": (-35,  35, -35,  35, -35,  35,  40, -40),
    "C": ( 27, -27,  27, -27,  27, -27,  40, -40),
    "D": (-40,  40,  27, -27,  27, -27,  55, -55),
    "E": ( 59, -59,  59, -59,  59, -59,  55, -55),
    "F": ( 55, -55, -35,  35, -35,  35, -10, -85),
    "G": (-40,  40,  90, -90,  90, -90, -30,  30),
    "H": (-40,  40, -40,  40,  90, -90,  75,  -5),
    "I": ( 90, -90,  90, -90,  90, -90,  75,  -5),  # approx: pinky unavailable
    "J": ( 90, -90,  90, -90,  90, -90,  75,  -5),  # approx: I + hook motion
    "K": (-40,  40,  -4,   4,  90, -90,   0,   0),
    "L": (-35,  35,  90, -90,  90, -90,  -4,  90),
    "M": ( 59, -59,  59, -59,  59, -59,  75,  -5),
    "N": ( 59, -59,  59, -59,  90, -90,  75,  -5),
    "O": ( 27, -27,  27, -27,  27, -27, -10, -85),
    "P": (-40,  40,  -4,   4,  90, -90,   0,   0),  # = K; wrist motion missing
    "Q": (-40,  40,  90, -90,  90, -90, -30,  30),  # = G; wrist motion missing
    "R": (-40,  40, -30,  30,  90, -90,  75,  -5),
    "S": ( 90, -90,  90, -90,  90, -90,  75,  -5),
    "T": ( 59, -59,  90, -90,  90, -90,   0,   0),
    "U": (-35,  35, -35,  35,  90, -90,  90, -90),
    "V": (-65,  15, -15,  65,  90, -90,  90, -90),
    "W": (-90,   0, -32,  32,  -4,  90,  55, -55),
    "X": (-10,  80,  90, -90,  90, -90,  75,  -5),
    "Y": ( 90, -90,  90, -90,  90, -90,  -4,  90),  # approx: pinky unavailable
    "Z": (-40,  40,  90, -90,  90, -90,  75,  -5),  # = G handshape; Z motion missing
}
Notes
- All 26 letters are present — nothing omitted.
- I, J, Y are best-effort: without a pinky servo they read as fist-with-thumb variants, not correct ASL shapes. J and Z also need a separate motion animation; a static tuple can't express the hook or Z stroke.
- K = P, G = Q, Z ≈ G, and U/H differ numerically here but still lack the wrist-orientation distinction from matrix 1.
- Values flagged earlier as extrapolated (curl arcs, thumbs (40,-40), (-30,30), (0,0), (55,-55), and F's middle/ring from the description rather than the demo's Perfect) still need hardware calibration.
This is display only — I'm in Plan mode, so nothing has been written to als-sign-matrix.md. Switch agents to apply it.
