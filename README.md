# signLang-rm2ah

Sign Language Training engine, Amazing hand (pollen) Teaches the Reachy Mini how to Sign.

Fingerspelling demo for a **left AmazingHand**: pose the hand into individual
letters, speak a prompt with Piper TTS, and loop through the alphabet for a
robot (Reachy Mini) to guess.

> **Hardware warning:** these scripts move real servos and leave torque enabled
> when they exit. Keep hands clear of the hand, and be ready to cut power.
> Power-cycling the hand releases torque.

## Files

| File | Purpose |
| --- | --- |
| `make-gest.py` | Drive left-hand servos 11–18 into a fingerspelling pose via `rustypot` (serial `/dev/ttyACM0`, 1,000,000 baud). `--list` prints the table; `--dry` prints angles without touching hardware. |
| `say.py` | One-shot or stdin-driven Piper TTS piped to `aplay`. |
| `gesture-loop.sh` | Original loop: ask first, then pose, then wait. No `--hint`. |
| `gest-loop2.sh` | Ask, pose, wait, then speak the label with `--hint`. |
| `gest-loop3.sh` | Pose, hold, ask with the label appended inline; no gap. |
| `gest-loop4.sh` | Pose, hold, ask, then wait `--gap` before the next letter. |

## Requirements

- Python 3
- `rustypot` (for the servo controller)
- `piper-tts` and `aplay` (ALSA) for speech; `espeak-ng` / `espeak` is an optional
  fallback in all four loop scripts
- An AmazingHand on `/dev/ttyACM0` (user must have serial-port access)

The existing `~/robot/talk/venv` environment has the needed Python packages:

```bash
source ~/robot/talk/venv/bin/activate
```

I am running Linux on a Chromebook, with USB serial to the AmazingHand
controller. The Chromebook talks and asks the Reachy Mini "what do you see?",
then the hand forms a sign. The RM is really dumb, so `--hint` was added: the
correct label is spoken too, so it can learn the signs.

The four loops are successive revisions of the same drill; see "Choosing a loop"
below.

## Quick start

```bash
# Inspect the letter table and a dry run (no hardware touched)
./make-gest.py --list
./make-gest.py a --dry

# Move the real hand
./make-gest.py open
./make-gest.py a --speed 4 --hold 1.5

# Speak a line
python3 say.py "what letter is this hand gesture?"

# One full pass of the alphabet, then exit
./gesture-loop.sh --once

# Endless shuffled loop, custom timing and prompt
./gesture-loop.sh --random --speed 3 --hold 2 --gap 6 \
  --prompt "reachy mini, what letter is this?"

# Gesture first, label in the question, then 8s for the robot to answer
./gest-loop4.sh --hint --gap 8
```

Run `./<script>.sh --help` for all options.

## Choosing a loop

All four loops use the same default letter order — readable letters first, then
thumb-dependent ones, then the shaky ones — and share `--random`, `--once`,
`--speed`, `--hold`, `--prompt`, and an explicit list of letters where
supported. What changed between revisions is **when the question is spoken**,
**where the training label goes**, and **how Ctrl-C is handled**:

| Script | Per-letter sequence | `--hint` | Timing knobs |
| --- | --- | --- | --- |
| `gesture-loop.sh` | ask → 0.3s → pose → wait | not supported | `--hold`, `--gap` |
| `gest-loop2.sh` | ask → 0.3s → pose → wait → label | separate line after the gap: "This is letter X." | `--hold`, `--gap` |
| `gest-loop3.sh` | pose (3s hold) → ask → next | appended to the question: "…What letter is this hand gesture? This is letter X." | `--hold` only (no `--gap`) |
| `gest-loop4.sh` | pose (2s hold) → ask → wait → next | appended to the question | `--hold`, `--gap` (default 8s) |

`gest-loop2.sh` also respelled the prompt as "reach-ee mini" so Piper
pronounces the name correctly, and replaced the simple `trap open_hand` with a
cleanup that kills the in-flight child and its `aplay` subprocess before
opening the hand, exiting 130 on Ctrl-C. Loops 3 and 4 keep that cleanup.

In short: use `gesture-loop.sh` for the original ask-then-pose demo,
`gest-loop2.sh` for question-then-correction training, `gest-loop3.sh` for a
fast pose-visible drill, and `gest-loop4.sh` when you want the robot to have
time to answer before the next gesture.

## Voice model

`say.py` looks for a Piper voice in this order:

1. `--model /path/to/voice.onnx`
2. `$PIPER_MODEL`
3. `./piper/en_US-lessac-medium.onnx`
4. `~/robot/talk/piper/en_US-lessac-medium.onnx`

Voice files are intentionally not tracked in this repository.

## Notes and known limitations

- Supported letters: A–H, K–L, M–O, P–S, T–W, X, Z (23 poses, 19 distinct shapes).
- `I`, `J`, and `Y` are omitted — they need a pinky.
- `P` = `K`, `Q` = `G`, `Z` = `G`, and `U` = `H` until wrist/index motion is added;
  `R` is an approximation.
- `MIDDLE_POS` in `make-gest.py` is the author's placeholder offsets. Real
  offsets must be measured (`get_zeros`) before poses are accurate; clamping is
  expected until then.
- The loops default to 20 of the 23 letters: `P`, `Q` and `R` are left out of the
  rotation. Pass them explicitly to include them, e.g. `./gest-loop4.sh P Q R`.
- A file lock at `/tmp/opencode/amazinghand.lock` prevents two `make-gest.py`
  processes from fighting over the hand.
