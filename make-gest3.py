#!/usr/bin/env python3
#signLang-rm2ah/make-gest3.py
"""
make-gest3.py -- drive the LEFT AmazingHand into one fingerspelling letter.

    ./make-gest3.py --list              # 26 x 8 table (AH has no pinky servos)
    ./make-gest3.py --list -v           # + commanded degrees + raw ticks + duplicates
    ./make-gest3.py A                   # move once, quiet
    ./make-gest3.py A -v                # every servo + bus readback + verdict
    ./make-gest3.py A -vv               # + register dump
    ./make-gest3.py A --dry -v          # table only, no serial
    ./make-gest3.py --probe             # per-ID survey, no motion
    ./make-gest3.py open

Left hand: index 15,16 / middle 13,14 / ring 11,12 / thumb 17,18.
Commanded angle = clamp(delta + MiddlePos[i], +/-limit).
Torque is left ON at exit so the letter stays held.

Matrix 3 has 8 values per letter (no pinky hardware):
    Index1, Index2, Middle1, Middle2, Ring1, Ring2, Thumb1, Thumb2.
I/J/Y are hardware-limited approximations. J and Z also need motion;
K/P, G/Q and U/H need wrist orientation to be distinguished.
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

MIDDLE_POS = [3, -3, -1, -10, 5, 2, -7, 3]   # PLACEHOLDER (author's values)

SERVOS = [15, 16, 13, 14, 11, 12, 17, 18]
LABELS = ["index1", "index2", "middle1", "middle2",
          "ring1", "ring2", "thumb1", "thumb2"]

LIMIT_DEG = 90.0
DEG_PER_STEP = 300.0 / 1024.0
RAD_PER_STEP = math.radians(300.0) / 1024.0
CENTER = 511

__version__ = "2.0"

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
    "I": ( 90, -90,  90, -90,  90, -90,  75,  -5),
    "J": ( 90, -90,  90, -90,  90, -90,  75,  -5),
    "K": (-40,  40,  -4,   4,  90, -90,   0,   0),
    "L": (-35,  35,  90, -90,  90, -90,  -4,  90),
    "M": ( 59, -59,  59, -59,  59, -59,  75,  -5),
    "N": ( 59, -59,  59, -59,  90, -90,  75,  -5),
    "O": ( 27, -27,  27, -27,  27, -27, -10, -85),
    "P": (-40,  40,  -4,   4,  90, -90,   0,   0),
    "Q": (-40,  40,  90, -90,  90, -90, -30,  30),
    "R": (-40,  40, -30,  30,  90, -90,  75,  -5),
    "S": ( 90, -90,  90, -90,  90, -90,  75,  -5),
    "T": ( 59, -59,  90, -90,  90, -90,   0,   0),
    "U": (-35,  35, -35,  35,  90, -90,  90, -90),
    "V": (-65,  15, -15,  65,  90, -90,  90, -90),
    "W": (-90,   0, -32,  32,  -4,  90,  55, -55),
    "X": (-10,  80,  90, -90,  90, -90,  75,  -5),
    "Y": ( 90, -90,  90, -90,  90, -90,  -4,  90),
    "Z": (-40,  40,  90, -90,  90, -90,  75,  -5),
}

OPEN = (-35, 35, -35, 35, -35, 35, -35, 35)

NOTES = {
    "I": "approx: no pinky servo on AH",
    "J": "approx: I shape + downward hook motion needed",
    "Y": "approx: no pinky servo on AH",
    "K": "== P handshape (needs wrist orientation)",
    "P": "== K handshape (needs wrist orientation)",
    "G": "== Q handshape (needs wrist orientation)",
    "Q": "== G handshape (needs wrist orientation)",
    "U": "H-like handshape (needs wrist orientation)",
    "Z": "G-like handshape; Z stroke motion needed",
    "S": "== I/J handshape here (no pinky)",
    "R": "fake cross, reads like U",
}

LETTERS = sorted(POSES)

# SCS0009 registers, big-endian (see scs09.md)
REG = {"min_limit": 9, "max_limit": 11, "torque": 40, "goal": 42,
       "speed": 46, "lock": 48, "present": 56, "moving": 66,
       "voltage": 62, "temp": 63}


# ---------------------------------------------------------------- table

def to_raw(deg):
    return int(round(CENTER + deg / DEG_PER_STEP))


def raw_to_deg(raw):
    return (raw - CENTER) * DEG_PER_STEP


def resolve(pose, limit=LIMIT_DEG, thumb_limit=LIMIT_DEG):
    """delta tuple -> (commanded degrees, clamped flags, raw ticks)"""
    cmd, clamped, raw = [], [], []
    for i, delta in enumerate(pose):
        want = delta + MIDDLE_POS[i]
        cap = thumb_limit if i >= 6 else limit
        got = max(-cap, min(cap, want))
        cmd.append(got)
        clamped.append(abs(got - want) > 1e-9)
        raw.append(to_raw(got))
    return cmd, clamped, raw


def shape_index(limit=LIMIT_DEG, thumb_limit=LIMIT_DEG):
    idx = {}
    for name in LETTERS:
        key = tuple(round(v, 1) for v in
                    resolve(POSES[name], limit, thumb_limit)[0])
        idx.setdefault(key, []).append(name)
    return idx


def print_gesture(name, pose, limit=LIMIT_DEG, thumb_limit=LIMIT_DEG):
    """The 8-servo matrix for one gesture. Always all eight rows."""
    cmd, clamped, raw = resolve(pose, limit, thumb_limit)
    print(f"=== gesture {name}   (limit {limit:g}, thumb {thumb_limit:g}) ===")
    print(f"  {'servo':<9}{'id':>4}{'delta':>7}{'off':>5}{'want':>8}"
          f"{'cmd':>8}{'clamp':>7}{'raw':>6}   {'C':>6}{'S':>7}{'|S|+|C|':>9}")
    for i, sid in enumerate(SERVOS):
        want = pose[i] + MIDDLE_POS[i]
        if i % 2 == 0:
            curl = (cmd[i] - cmd[i + 1]) / 2.0
            swing = (cmd[i] + cmd[i + 1]) / 2.0
            cs = f"{curl:>6.1f}{swing:>7.1f}{abs(swing) + abs(curl):>9.1f}"
        else:
            cs = " " * 22
        print(f"  {LABELS[i]:<9}{sid:>4}{pose[i]:>7}{MIDDLE_POS[i]:>+5}"
              f"{want:>8.1f}{cmd[i]:>8.1f}{'YES' if clamped[i] else 'no':>7}"
              f"{raw[i]:>6}   {cs}")
    twins = [x for x in shape_index(limit, thumb_limit)
             .get(tuple(round(v, 1) for v in cmd), []) if x != name]
    if twins:
        print(f"  shape identical to: {', '.join(twins)}")
    if any(clamped):
        print("  note: clamp fired -- MiddlePos is still the author's placeholder")


def print_list(verbose=False, limit=LIMIT_DEG, thumb_limit=LIMIT_DEG):
    print(f"left hand  port {PORT_DEFAULT}  {BAUDRATE} baud")
    print(f"MiddlePos {MIDDLE_POS}   limit {limit:g}   thumb {thumb_limit:g}\n")
    hdr = f"{'letter':^7}" + "".join(f"{l:>8}" for l in LABELS)
    print("deltas (degrees added to MiddlePos):")
    print(hdr)
    print("-" * len(hdr))
    for name in LETTERS:
        print(f"{name:^6} " + "".join(f"{v:>8}" for v in POSES[name])
              + f"  {NOTES.get(name, '')}")

    if not verbose:
        idx = shape_index(limit, thumb_limit)
        print(f"\n{len(LETTERS)} letters, {len(idx)} distinct shapes "
              "(no pinky column on AH; I/J/Y are approximations)")
        return

    print("\ncommanded degrees (delta + MiddlePos, clamped):")
    print(hdr)
    for name in LETTERS:
        cmd = resolve(POSES[name], limit, thumb_limit)[0]
        print(f"{name:^6} " + "".join(f"{v:>8.1f}" for v in cmd))

    print("\nraw ticks (511 + deg / 0.29296875):")
    print(hdr)
    for name in LETTERS:
        raw = resolve(POSES[name], limit, thumb_limit)[2]
        print(f"{name:^6} " + "".join(f"{v:>8d}" for v in raw))

    idx = shape_index(limit, thumb_limit)
    dup = [v for v in idx.values() if len(v) > 1]
    print(f"\n{len(LETTERS)} letters, {len(idx)} distinct shapes")
    for v in dup:
        print("  identical:", "/".join(v))


# ---------------------------------------------------------------- bus

def read_reg(c, sid, addr, size):
    """Unsigned big-endian register read. None on no reply."""
    fn = getattr(c, "read_raw_data", None)
    if fn is None:
        return None
    try:
        d = fn(sid, addr, size)
    except Exception:
        return None
    if d is None:
        return None
    if isinstance(d, (bytes, bytearray, list, tuple)):
        v = 0
        for b in d:
            v = (v << 8) | (int(b) & 0xFF)
        return v
    return int(d)


def read_present(c, sid):
    r = read_reg(c, sid, REG["present"], 2)
    if r is not None:
        return r
    try:
        return int(round(CENTER + c.read_present_position(sid) / RAD_PER_STEP))
    except Exception:
        return None


def write_reg(c, sid, addr, value, size):
    fn = getattr(c, "write_raw_data", None)
    if fn is None:
        return False
    data = [((value >> (8 * (size - 1 - i))) & 0xFF) for i in range(size)]
    try:
        fn(sid, addr, data)
        return True
    except Exception:
        return False


def snapshot(c, title, show_limits=False):
    print(f"--- {title} ---")
    head = (f"  {'id':>3}{'present':>9}{'deg':>8}{'goal':>7}"
            f"{'torque':>7}{'V':>6}{'T':>5}")
    if show_limits:
        head += f"{'min':>6}{'max':>6}{'lock':>6}"
    print(head)
    out = {}
    for sid in SERVOS:
        p = read_present(c, sid)
        out[sid] = p
        if p is None:
            print(f"  {sid:>3}   ABSENT (no reply)")
            continue
        g = read_reg(c, sid, REG["goal"], 2)
        t = read_reg(c, sid, REG["torque"], 1)
        v = read_reg(c, sid, REG["voltage"], 1)
        tp = read_reg(c, sid, REG["temp"], 1)
        line = (f"  {sid:>3}{p:>9}{raw_to_deg(p):>8.1f}"
                f"{g if g is not None else -1:>7}"
                f"{t if t is not None else -1:>7}"
                f"{(v / 10.0) if v is not None else 0:>6.1f}"
                f"{tp if tp is not None else -1:>5}")
        if show_limits:
            lo = read_reg(c, sid, REG["min_limit"], 2)
            hi = read_reg(c, sid, REG["max_limit"], 2)
            lk = read_reg(c, sid, REG["lock"], 1)
            line += (f"{lo if lo is not None else -1:>6}"
                     f"{hi if hi is not None else -1:>6}"
                     f"{lk if lk is not None else -1:>6}")
        print(line)
    return out


def write_speed(c, sid, args):
    if args.raw_write:
        sr = args.speed_raw if args.speed_raw is not None else 0
        write_reg(c, sid, REG["speed"], sr, 2)
        return sr
    c.write_goal_speed(sid, args.speed)
    return int(round(args.speed / RAD_PER_STEP))


def write_pos(c, sid, deg, args):
    raw = to_raw(deg)
    if args.raw_write:
        if not write_reg(c, sid, REG["goal"], raw, 2):
            raise RuntimeError("write_raw_data not available; drop --raw-write")
    else:
        c.write_goal_position(sid, math.radians(deg))
    return raw


def send(c, degs, args, verbose=False):
    for sid in SERVOS:
        c.write_torque_enable(sid, 1)
    time.sleep(0.05)
    for i, sid in enumerate(SERVOS):
        sr = write_speed(c, sid, args)
        if verbose:
            print(f"  write id={sid:<2} speed -> raw {sr}")
        time.sleep(0.0002)
    for i, sid in enumerate(SERVOS):
        raw = write_pos(c, sid, degs[i], args)
        if verbose:
            print(f"  write id={sid:<2} {degs[i]:>7.1f} deg -> raw {raw}")
        time.sleep(0.0002)


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


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(
        description="Drive the left AmazingHand into a fingerspelling letter.")
    ap.add_argument("--version", action="version",
                    version=f"%(prog)s {__version__}")
    ap.add_argument("letter", nargs="?",
                    help="A-Z (I, J, Y are approximations) or 'open'")
    ap.add_argument("-v", "--verbose", action="count", default=0,
                    help="all 8 servos + bus readback (-vv = registers)")
    ap.add_argument("--list", action="store_true", help="print the table and exit")
    ap.add_argument("--probe", action="store_true", help="read the bus, no motion")
    ap.add_argument("--dry", action="store_true", help="print angles, no hardware")
    ap.add_argument("--raw-write", action="store_true",
                    help="write goal/speed as raw ticks, bypass rustypot")
    ap.add_argument("--speed", type=float, default=4.0, help="rad/s (default 4)")
    ap.add_argument("--speed-raw", type=int, default=None,
                    help="raw goal_speed with --raw-write (0 = max)")
    ap.add_argument("--hold", type=float, default=1.0,
                    help="seconds after moving (default 1.0)")
    ap.add_argument("--wait", type=float, default=0.0,
                    help="poll present position up to N s for arrival")
    ap.add_argument("--limit", type=float, default=LIMIT_DEG,
                    help="cap on every commanded angle (default 90)")
    ap.add_argument("--thumb-limit", type=float, default=LIMIT_DEG,
                    help="cap for servos 17/18 (default 90)")
    ap.add_argument("--max-jump", type=float, default=120.0,
                    help="split a single move larger than this via midpoint "
                         "(0 = off, default 120)")
    ap.add_argument("--port", default=PORT_DEFAULT)
    args = ap.parse_args()

    if args.list:
        print_list(args.verbose > 0, args.limit, args.thumb_limit)
        return 0

    if not args.letter and not args.probe:
        ap.error("give a letter, 'open', --probe or --list")

    key = (args.letter or "").strip().upper()
    if key == "OPEN":
        pose, name = OPEN, "open"
    elif key in POSES:
        pose, name = POSES[key], key
    elif key:
        print(f"unknown gesture {args.letter!r}. valid: "
              f"{' '.join(LETTERS)} open", file=sys.stderr)
        return 2
    else:
        pose, name = None, None

    if pose and args.verbose:
        print_gesture(name, pose, args.limit, args.thumb_limit)
        if NOTES.get(key):
            print(f"  note: {key} {NOTES[key]}")

    if args.dry:
        if pose and not args.verbose:
            print_gesture(name, pose, args.limit, args.thumb_limit)
        return 0

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
        print(f"port open failed {args.port}: {type(e).__name__}: {e}",
              file=sys.stderr)
        lock.close()
        return 1

    if args.probe:
        snapshot(c, "probe", show_limits=args.verbose > 0)
        p1 = read_present(c, 1)
        print(f"  ID   1   " + ("ABSENT (good)" if p1 is None
                                else f"STILL ASSIGNED pos={p1}"))
        lock.close()
        return 0

    before = snapshot(c, "bus before", show_limits=args.verbose > 1) \
        if args.verbose else {sid: read_present(c, sid) for sid in SERVOS}

    cmd, clamped, targets = resolve(pose, args.limit, args.thumb_limit)

    travel = [abs(cmd[i] - raw_to_deg(before[SERVOS[i]]))
              for i in range(8) if before.get(SERVOS[i]) is not None]
    worst = max(travel) if travel else 0.0

    if args.max_jump > 0 and worst > args.max_jump:
        mid = [(cmd[i] + (raw_to_deg(before[SERVOS[i]])
                          if before.get(SERVOS[i]) is not None else cmd[i])) / 2.0
               for i in range(8)]
        if args.verbose:
            print(f"  guard: max travel {worst:.0f} deg > {args.max_jump:g} "
                  f"-> midpoint first")
        send(c, mid, args, verbose=args.verbose)
        time.sleep(0.4)

    send(c, cmd, args, verbose=args.verbose)

    if args.wait:
        t0 = time.time()
        err = 999
        while time.time() - t0 < args.wait:
            cur = {sid: read_present(c, sid) for sid in SERVOS}
            err = max((abs(cur[sid] - targets[i])
                       for i, sid in enumerate(SERVOS)
                       if cur[sid] is not None), default=999)
            if err <= 3:
                break
            time.sleep(0.2)
        if args.verbose:
            print(f"  arrival: {time.time() - t0:.2f}s, worst {err} steps")
    else:
        time.sleep(args.hold)

    after = {sid: read_present(c, sid) for sid in SERVOS}
    moved = 0

    if args.verbose:
        print("--- bus after ---")
        print(f"  {'id':>3}{'target':>8}{'goal_rb':>9}{'present':>9}"
              f"{'deg':>8}{'err':>6}{'moved':>7}  verdict")
        answered = torque_ok = goal_ok = arrived = 0
        for i, sid in enumerate(SERVOS):
            p = after[sid]
            if p is None:
                print(f"  {sid:>3}   ABSENT")
                continue
            answered += 1
            g = read_reg(c, sid, REG["goal"], 2)
            t = read_reg(c, sid, REG["torque"], 1)
            torque_ok += (t == 1)
            err = targets[i] - p
            d = (p - before[sid]) if before.get(sid) is not None else 0
            moved = max(moved, abs(d))
            goal_ok += (g is not None and abs(g - targets[i]) <= 2)
            arrived += (abs(err) <= 3)
            print(f"  {sid:>3}{targets[i]:>8}{g if g is not None else -1:>9}"
                  f"{p:>9}{raw_to_deg(p):>8.1f}{err:>6}{d:>+7}"
                  f"  {'ok' if abs(err) <= 3 else 'SHORT'}")
        print(f"VERDICT: answered {answered}/8, torque {torque_ok}/8, "
              f"goal readback {goal_ok}/8, at target {arrived}/8")
        if answered < 8:
            print("  -> missing servos: run --probe, check ID assignment")
        elif torque_ok < 8:
            print("  -> torque not on: reg 40")
        elif goal_ok < 8:
            print("  -> writes did not land: goal reg != target")
        elif arrived < 8:
            print("  -> landed but not at target: too slow or stalled")
        else:
            print("  -> all 8 servos at target")
    else:
        for sid in SERVOS:
            p = after[sid]
            if p is not None and before.get(sid) is not None:
                moved = max(moved, abs(p - before[sid]))
        print(f"{name}: sent to 8 servos (use -v to verify)")

    lock.close()

    if worst > 10 and moved <= 3:
        print("FAIL: commanded a move but nothing moved", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
