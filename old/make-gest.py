#!/usr/bin/env python3
"""
make-gest -- drive the LEFT AmazingHand into one fingerspelling letter.

    ./make-gest.py a
    ./make-gest.py a --dry       # print angles + raw steps, touch no hardware
    ./make-gest.py --list        # print the whole table
    ./make-gest.py open          # open/neutral hand
    ./make-gest.py a --speed 4 --hold 1.5

Values are degrees ADDED to MiddlePos (same convention as the demo's Move_*).
Commanded angle = clamp(delta + MiddlePos[i], +/-90).

Left hand only:  index 15,16 / middle 13,14 / ring 11,12 / thumb 17,18
Torque is enabled on 11..18 every run and left ON at exit, so the letter
stays held. Torque is lost on power cycle, never on script exit.
"""

import argparse
import fcntl
import math
import os
import sys
import time

PORT_DEFAULT = "/dev/ttyACM0"
BAUDRATE = 1000000
LOCK_PATH = "/tmp/opencode/amazinghand.lock"

# MiddlePos slot order == SERVOS order below
MIDDLE_POS = [3, -3, -1, -10, 5, 2, -7, 3]   # PLACEHOLDER (author's values)

SERVOS = [15, 16, 13, 14, 11, 12, 17, 18]
LABELS = ["index1", "index2", "middle1", "middle2",
          "ring1", "ring2", "thumb1", "thumb2"]

LIMIT_DEG = 90.0
DEG_PER_STEP = 300.0 / 1024.0        # 0.29296875 deg per raw step

# Row order: index1, index2, middle1, middle2, ring1, ring2, thumb1, thumb2
POSES = {
    "A": ( 90,-90,  90,-90,  90,-90, -15,-15),
    "B": (  0,  0,   0,  0,   0,  0, -35,-55),
    "C": ( 40,-40,  40,-40,  40,-40,  10,-70),
    "D": (  0,  0,  50,-50,  50,-50,  15,-85),
    "E": ( 65,-65,  65,-65,  65,-65,   5,-85),
    "F": ( 50,-50,   0,  0,   0,  0,   5,-85),
    "G": (  0,  0,  90,-90,  90,-90,  10, 10),
    "H": (  0,  0,   0,  0,  90,-90,  -5,-55),
    "K": (-30,-30, -30,-30,  90,-90, -10,-10),
    "L": (  0,  0,  90,-90,  90,-90,  45, 45),
    "M": ( 80,-80,  80,-80,  80,-80,  -5,-85),
    "N": ( 80,-80,  80,-80,  80,-80,   5,-75),
    "O": ( 65,-65,  65,-65,  65,-65,  25,-85),
    "P": (-30,-30, -30,-30,  90,-90, -10,-10),
    "Q": (  0,  0,  90,-90,  90,-90,  10, 10),
    "R": ( -5, -5,   5,  5,  90,-90,  -5,-55),
    "S": ( 88,-88,  88,-88,  88,-88,  -5,-85),
    "T": ( 85,-85,  85,-85,  85,-85,   0,-70),
    "U": (  0,  0,   0,  0,  90,-90,  -5,-55),
    "V": (-40,-40,  40, 40,  90,-90,  -5,-55),
    "W": (-40,-40,   0,  0,  40, 40, -20,-40),
    "X": ( 50,-50,  90,-90,  90,-90,   0,-50),
    "Z": (  0,  0,  90,-90,  90,-90,  10, 10),
}

# demo's verified OpenHand
OPEN = (-35, 35, -35, 35, -35, 35, -35, 35)

NOTES = {
    "P": "== K (needs wrist)",
    "Q": "== G (needs wrist)",
    "Z": "== G (needs index motion)",
    "U": "== H (needs wrist)",
    "R": "fake cross, reads like U",
    "D": "thumb reach", "E": "thumb opposition", "F": "thumb reach",
    "M": "thumb opposition", "N": "thumb opposition", "O": "thumb reach",
    "S": "thumb opposition",
}

LETTERS = sorted(POSES)


def clamp(v, lo=-LIMIT_DEG, hi=LIMIT_DEG):
    return max(lo, min(hi, v))


def resolve(pose):
    """delta tuple -> (commanded degrees, clamped flags, raw steps)"""
    cmd, clamped, raw = [], [], []
    for i, delta in enumerate(pose):
        want = delta + MIDDLE_POS[i]
        got = clamp(want)
        cmd.append(got)
        clamped.append(abs(got - want) > 1e-9)
        raw.append(int(round(511 + got / DEG_PER_STEP)))
    return cmd, clamped, raw


def print_table(pose, name):
    cmd, clamped, raw = resolve(pose)
    print(f"gesture {name}")
    print(f"  {'servo':<9}{'id':>4}{'delta':>8}{'+off':>8}{'cmd':>8}{'raw':>7}  flag")
    for i, sid in enumerate(SERVOS):
        flag = "WARN clamp" if clamped[i] else ""
        print(f"  {LABELS[i]:<9}{sid:>4}{pose[i]:>8}{MIDDLE_POS[i]:>8}"
              f"{cmd[i]:>8.1f}{raw[i]:>7}  {flag}")
    if any(clamped):
        print("  note: MiddlePos is still the author's placeholder; "
              "clamping is expected until get_zeros runs.")


def list_all():
    print(f"left hand  port {PORT_DEFAULT}  {BAUDRATE} baud")
    print(f"MiddlePos {MIDDLE_POS}\n")
    hdr = f"{'letter':^8}" + "".join(f"{l:>8}" for l in LABELS)
    print(hdr)
    print("-" * len(hdr))
    for name in LETTERS:
        row = "".join(f"{v:>8}" for v in POSES[name])
        note = NOTES.get(name, "")
        print(f"{name:^6}  {row}  {note}")
    print("\nI, J, Y omitted (need a pinky). 23 letters, 19 distinct shapes.")


def acquire_lock():
    os.makedirs(os.path.dirname(LOCK_PATH), exist_ok=True)
    fh = open(LOCK_PATH, "w")
    for _ in range(20):
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fh
        except BlockingIOError:
            time.sleep(0.25)
    print("error: another make-gest holds the hand", file=sys.stderr)
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser(
        add_help=True,
        description="Drive the left AmazingHand into a fingerspelling letter.")
    ap.add_argument("letter", nargs="?", help="letter A-Z (I, J, Y unsupported) or 'open'")
    ap.add_argument("--dry", action="store_true", help="print angles, no hardware")
    ap.add_argument("--list", action="store_true", help="print the table and exit")
    ap.add_argument("--speed", type=int, default=4, help="servo speed 1-7 (default 4)")
    ap.add_argument("--hold", type=float, default=1.0, help="seconds after moving (default 1.0)")
    ap.add_argument("--port", default=PORT_DEFAULT)
    args = ap.parse_args()

    if args.list:
        list_all()
        return 0

    if not args.letter:
        ap.error("give a letter, 'open', or --list")

    key = args.letter.strip().upper()
    if key == "OPEN":
        pose, name = OPEN, "open"
    elif key in POSES:
        pose, name = POSES[key], key
    else:
        print(f"unknown gesture {args.letter!r}. valid: "
              f"{' '.join(LETTERS)} open", file=sys.stderr)
        return 2

    if NOTES.get(key):
        print(f"note: {key} {NOTES[key]}")

    if args.dry:
        print_table(pose, name)
        return 0

    cmd, clamped, _ = resolve(pose)
    if any(clamped):
        print("WARN clamp: " + ", ".join(
            f"{LABELS[i]} {cmd[i]:.1f}" for i in range(8) if clamped[i]))

    try:
        from rustypot import Scs0009PyController
    except Exception as e:
        print(f"rustypot import failed: {e}", file=sys.stderr)
        return 1

    lock = acquire_lock()
    try:
        c = Scs0009PyController(serial_port=args.port,
                                baudrate=BAUDRATE, timeout=0.5)
    except Exception as e:
        print(f"port open failed {args.port}: {type(e).__name__}: {e}", file=sys.stderr)
        lock.close()
        return 1

    speed = max(1, min(7, args.speed))

    for sid in SERVOS:
        c.write_torque_enable(sid, 1)
    time.sleep(0.05)

    for i, sid in enumerate(SERVOS):
        c.write_goal_speed(sid, speed)
        time.sleep(0.0002)
    for i, sid in enumerate(SERVOS):
        c.write_goal_position(sid, math.radians(cmd[i]))
        time.sleep(0.0002)

    time.sleep(args.hold)
    print(f"{name}: held (torque on)")
    lock.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
