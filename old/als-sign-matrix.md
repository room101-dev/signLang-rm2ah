American Sign Language (ASL) fingerspelling uses 26 one-handed handshapes (A–Z) held near shoulder height, usually with the palm facing forward. Most letters are static, while J and Z include motion. You can explore interactive demos and practice clips on Ziggy ASL.

ASL Fingerspelling Finger Position Matrix (A–Z)


Letter	Thumb	Index Finger	Middle Finger	Ring Finger	Pinky Finger	Palm / Motion Notes
A	Rests beside index finger	Curled into palm	Curled into palm	Curled into palm	Curled into palm	Closed fist; palm forward
B	Tucked across palm	Extended straight up	Extended straight up	Extended straight up	Extended straight up	Fingers together; palm forward
C	Curved to meet fingers	Curved in a "C" arc	Curved in a "C" arc	Curved in a "C" arc	Curved in a "C" arc	Open "C" shape; palm to side/forward
D	Touches middle/ring/pinky tips	Extended straight up	Curved to touch thumb	Curved to touch thumb	Curved to touch thumb	Circle with thumb & lower fingers; palm forward
E	Tucked across front of fingers	Bent down toward thumb	Bent down toward thumb	Bent down toward thumb	Bent down toward thumb	Fingertips touch/near thumb; palm forward
F	Touches index fingertip	Touches thumb tip (circle)	Extended straight up	Extended straight up	Extended straight up	"OK"-style circle; other 3 fingers up; palm forward
G	Parallel to index, slightly below	Pointed horizontally forward	Curled into palm	Curled into palm	Curled into palm	Palm faces toward you (sideways/inward)
H	Tucked under middle/ring/pinky	Extended horizontally forward	Extended horizontally forward	Curled into palm	Curled into palm	Two fingers horizontal together; palm toward you
I	Crosses over curled fingers	Curled into palm	Curled into palm	Curled into palm	Extended straight up	Only pinky extended; palm forward
J	Crosses over curled fingers	Curled into palm	Curled into palm	Curled into palm	Extended up, hooks down	Same as I, plus draw a downward "J" hook
K	Placed between index & middle	Extended straight up	Angled forward/up	Curled into palm	Curled into palm	Thumb touches middle finger; palm forward
L	Extended out to side (90°)	Extended straight up	Curled into palm	Curled into palm	Curled into palm	Clear "L" shape; palm forward
M	Tucked under index, middle, ring	Draped over thumb	Draped over thumb	Draped over thumb	Curled into palm	Three fingers over thumb
N	Tucked under index & middle	Draped over thumb	Draped over thumb	Curled into palm	Curled into palm	Two fingers over thumb
O	Touches fingertips to form ring	Curved to meet thumb	Curved to meet thumb	Curved to meet thumb	Curved to meet thumb	All fingers curve into an "O"
P	Touches middle finger	Pointed downward	Angled downward	Curled into palm	Curled into palm	Like K, but hand/fingers point downward
Q	Parallel to index, below	Pointed downward	Curled into palm	Curled into palm	Curled into palm	Like G, but pointed downward
R	Crosses over ring/pinky	Extended up, middle crosses over	Crossed over front of index	Curled into palm	Curled into palm	Index and middle fingers crossed
S	Crossed over front of curled fingers	Curled into palm	Curled into palm	Curled into palm	Curled into palm	Fist with thumb across front of fingers
T	Tucked between index & middle	Bent down over thumb	Curled into palm	Curled into palm	Curled into palm	Thumb pokes out between index and middle
U	Holds down ring & pinky	Extended straight up	Extended straight up	Curled into palm	Curled into palm	Index and middle straight up together
V	Holds down ring & pinky	Extended up, spread apart	Extended up, spread apart	Curled into palm	Curled into palm	Index and middle spread in a "V"
W	Holds down pinky	Extended up, spread	Extended up, spread	Extended up, spread	Curled into palm	Three fingers extended and spread
X	Holds down middle/ring/pinky	Bent/hooked like a hook	Curled into palm	Curled into palm	Curled into palm	Index finger forms a hook
Y	Extended out to side	Curled into palm	Curled into palm	Curled into palm	Extended out/up	Thumb and pinky extended ("hang loose" shape)
Z	Holds down middle/ring/pinky	Extended forward, draws "Z"	Curled into palm	Curled into palm	Curled into pa 
Trace a "Z" in the air with index tip

...


Servo position columns (fixed order): Index1, Index2, Middle1, Middle2, Ring1, Ring2, Thumb1, Thumb2.
Values are servo deltas added to MiddlePos, clamped to ±90.
Letter	Index1	Index2	Middle1	Middle2	Ring1	Ring2	Thumb1	Thumb2
A	90	-90	90	-90	90	-90	-15	-15
B	0	0	0	0	0	0	-35	-55
C	40	-40	40	-40	40	-40	10	-70
D	0	0	50	-50	50	-50	15	-85
E	65	-65	65	-65	65	-65	5	-85
F	50	-50	0	0	0	0	5	-85
G	0	0	90	-90	90	-90	10	10
H	0	0	0	0	90	-90	-5	-55
K	-30	-30	-30	-30	90	-90	-10	-10
L	0	0	90	-90	90	-90	45	45
M	80	-80	80	-80	80	-80	-5	-85
N	80	-80	80	-80	80	-80	5	-75
O	65	-65	65	-65	65	-65	25	-85
P	-30	-30	-30	-30	90	-90	-10	-10
Q	0	0	90	-90	90	-90	10	10
R	-5	-5	5	5	90	-90	-5	-55
S	88	-88	88	-88	88	-88	-5	-85
T	85	-85	85	-85	85	-85	0	-70
U	0	0	0	0	90	-90	-5	-55
V	-40	-40	40	40	90	-90	-5	-55
W	-40	-40	0	0	40	40	-20	-40
X	50	-50	90	-90	90	-90	0	-50
Z	0	0	90	-90	90	-90	10	10
I/J/Y omitted; old matrix not worth patching; TODO stands.


###

new python array

When you give the word, here’s the new Python array I’ll put in the new driver:
POSES = {
    "A":  (90,-90,  90,-90,  90,-90, -15,-15),
    "B":  (  0,  0,   0,  0,    0,  0,  -35,-55),
    "C":  ( 40,-40,  40,-40,  40,-40,  10,-70),
    "D":  (  0,  0,  50,-50,   50,-50,  15,-85),
    "E":  ( 65,-65,  65,-65,  65,-65,   5,-85),
    "F":  ( 50,-50,   0,  0,    0,  0,   5,-85),
    "G":  (  0,  0,  90,-90,   90,-90,  10,10),
    "H":  (  0,  0,   0,  0,   90,-90,  -5,-55),
    "I":  ( 90,-90,  90,-90,  90,-90,  -5,-85),
    "J":  ( 90,-90,  90,-90,  90,-90,  -5,-85),
    "K":  (-30,-30, -30,-30,  90,-90, -10,-10),
    "L":  (  0,  0,  90,-90,   90,-90,  45,45),
    "M":  ( 80,-80,  80,-80,  80,-80,  -5,-85),
    "N":  ( 80,-80,  80,-80,  80,-80,   5,-75),
    "O":  ( 65,-65,  65,-65,  65,-65,  25,-85),
    "P":  (-30,-30, -30,-30,  90,-90, -10,-10),
    "Q":  (  0,  0,  90,-90,   90,-90,  10,10),
    "R":  ( -5, -5,   5,  5,   90,-90,  -5,-55),
    "S":  ( 88,-88,  88,-88,  88,-88,  -5,-85),
    "T":  ( 85,-85,  85,-85,  85,-85,   0,-70),
    "U":  (  0,  0,   0,  0,   90,-90,  -5,-55),
    "V":  (-40,-40,  40, 40,   90,-90,  -5,-55),
    "W":  (-40,-40,   0,  0,   40, 40, -20,-40),
    "X":  ( 50,-50,  90,-90,   90,-90,   0,-50),
    "Y":  ( 90,-90,  90,-90,  90,-90,   45,45),
    "Z":  (  0,  0,  90,-90,   90,-90,   10,10),
}
