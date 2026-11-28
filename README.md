# signLang-rm2ah

**Version 2.0** — major revision of the first build (`old/`).

Sign-language fingerspelling training for a left AmazingHand (AH) teaching a
Reachy Mini (RM). The AH forms each letter while the loop speaks the prompt and
the correct label; the RM learns the mapping from label to pose.

Run this on the laptop connected to the AH and the Pi-4, not on the
development server.

> **Hardware warning:** these scripts move real servos and leave torque enabled
> when they exit. Keep hands clear of the hand, and be ready to cut power.
> Power-cycling the hand releases torque.

## Files

| File | Purpose |
| --- | --- |
| `make-gest3.py` | Current driver for left-hand servos 11–18 via `rustypot` (`/dev/ttyACM0`, 1,000,000 baud). 26 letters, 8 values per pose. `--list` prints the table; `--dry` prints angles without touching hardware. |
| `say.py` | One-shot or stdin-driven Piper TTS piped to `aplay`. |
| `gest-loop6.sh` | Training loop: pose, hold, speak prompt (optional label), wait, next letter. |
| `als-sign-matrix.md` | Letter descriptions, servo map, and the Python pose matrix. |
| `als-sign-array.md` | Array form of the pose data. |
| `old/` | Earlier drivers and loop revisions. |

Python files are not executable; always invoke them with `python3`.

## Requirements

- Python 3
- `rustypot` (servo controller)
- `piper-tts` and `aplay` (ALSA) for speech; `espeak-ng` / `espeak` is a fallback
- An AmazingHand on `/dev/ttyACM0` (user must have serial-port access)

The existing `~/robot/talk/venv` environment has the needed Python packages:

```bash
source ~/robot/talk/venv/bin/activate
```

The Chromebook talks over USB serial to the AH controller and speaks the prompt
and label so the RM can learn each sign.

## Quick start

```bash
# Inspect the table and dry-run a letter (no hardware touched)
python3 make-gest3.py --list
python3 make-gest3.py a --dry

# Move the real hand
python3 make-gest3.py open
python3 make-gest3.py a --speed 4 --hold 1.5

# Speak a line
python3 say.py "what letter is this hand gesture?"

# One full pass, then exit
bash gest-loop6.sh --once

# Endless shuffled loop, custom timing and prompt
bash gest-loop6.sh --random --speed 3 --hold 2 --gap 6 \
  --prompt "reachy mini, what letter is this?"

# Gesture first, label in the question, then 8s before the next letter
bash gest-loop6.sh --hint --gap 8
```

Run `bash gest-loop6.sh --help` for all options.

## Loop options

| Option | Effect |
| --- | --- |
| `--random`, `-r` | Shuffle letters each pass |
| `--once`, `-1` | One pass, then exit |
| `--hint`, `-H` | Append "This is letter X." to the prompt |
| `-v`, `--verbose` | Servo table and bus readback per letter |
| `--speed` | Servo speed (rad/s) |
| `--hold` | Seconds the pose is held |
| `--gap` | Seconds after the prompt before the next letter |
| `--prompt` | Override the spoken prompt |
| `a b c` | Explicit letter list instead of the alphabet |

## Voice model

`say.py` looks for a Piper voice in this order:

1. `--model /path/to/voice.onnx`
2. `$PIPER_MODEL`
3. `./piper/en_US-lessac-medium.onnx`
4. `~/robot/talk/piper/en_US-lessac-medium.onnx`

Voice files are intentionally not tracked in this repository.

## Notes

- All 26 letters are defined in `make-gest3.py`. AH has no pinky servo, so
  I/J/Y are approximations; J and Z also need motion that a static pose cannot
  express.
- `MIDDLE_POS` in `make-gest3.py` is the author's placeholder offsets. Real
  offsets must be measured (`get_zeros`) before poses are accurate; clamping is
  expected until then.
- A file lock at `/tmp/opencode/amazinghand.lock` prevents two `make-gest3.py`
  processes from fighting over the hand.
- Ctrl-C kills the in-flight child, opens the hand, and exits 130.
