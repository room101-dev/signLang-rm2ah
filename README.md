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
| `make-gest.py` | Drive left-hand servos 11–18 into a fingerspelling pose via `rustypot` (serial `/dev/ttyACM0`, 1,000,000 baud). |
| `say.py` | One-shot or stdin-driven Piper TTS piped to `aplay`. |
| `gesture-loop.sh` | Speak a prompt, pose one letter, pause, repeat. |

## Requirements

- Python 3
- `rustypot` (for the servo controller)
- `piper-tts` and `aplay` (ALSA) for speech; `espeak-ng` / `espeak` is an optional fallback in `gesture-loop.sh`
- An AmazingHand on `/dev/ttyACM0` (user must have serial-port access)

The existing `~/robot/talk/venv` environment has the needed Python packages:

Running linux, I am running on a chrome-book linux box, usb to AH controller; The chromebook is talking, asks the 'reachy mini' "what do you see?", then the AH forms a sign; Now the RM is really dumb, so I added the --hint arg, so it tells it what its seeing, so it can 'learn' the signs;

Newer versions will be in this folder, gest-loop2.sh, loop4.sh,  with newer args

```bash
source ~/robot/talk/venv/bin/activate
```

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
```

Run `./gesture-loop.sh --help` for all options.

## Voice model

`say.py` looks for a Piper voice in this order:

1. `--model /path/to/voice.onnx`
2. `$PIPER_MODEL`
3. `./piper/en_US-lessac-medium.onnx`
4. `~/robot/talk/piper/en_US-lessac-medium.onnx`

Voice files are intentionally not tracked in this repository.

## Notes and known limitations

- Supported letters: A–H, K–L, M–O, P–S, T–V, X, Z (23 poses, 19 distinct shapes).
- `I`, `J`, and `Y` are omitted — they need a pinky.
- `P` = `K`, `Q` = `G`, `Z` = `G`, and `U` = `H` until wrist/index motion is added;
  `R` is an approximation.
- `MIDDLE_POS` in `make-gest.py` is the author's placeholder offsets. Real
  offsets must be measured (`get_zeros`) before poses are accurate; clamping is
  expected until then.
- A file lock at `/tmp/opencode/amazinghand.lock` prevents two `make-gest.py`
  processes from fighting over the hand.
