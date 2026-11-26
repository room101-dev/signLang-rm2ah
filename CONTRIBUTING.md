# Contributing

## Setup

```bash
git clone https://github.com/room101-dev/signLang-rm2ah.git
cd signLang-rm2ah
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` contains the Python packages needed by the scripts. System
pieces are separate: `aplay` (ALSA) for Piper output, optional `espeak-ng` /
`espeak` fallback, serial-port access, and a local Piper voice model. A
`.venv/` created by the commands above is ignored and must not be committed.

Thanks for helping improve `signLang-rm2ah`.

## Safety first

These scripts move real servos on a left AmazingHand and leave torque enabled
when they exit. Before running anything that touches hardware:

- Read the hardware warning in `README.md`.
- Keep hands clear of the hand.
- Be ready to cut power.
- Power-cycle the hand to release torque.
- Use `--dry` or `--list` first when possible.

## Local checks without hardware

From the repository root, with Python 3 available:

```bash
python3 -m py_compile make-gest.py say.py
bash -n gesture-loop.sh gest-loop2.sh gest-loop3.sh gest-loop4.sh
./make-gest.py --list
./make-gest.py a --dry
```

`python3 -m py_compile` may create `__pycache__`; do not commit it.

The author's environment note says `~/robot/talk/venv` has the needed Python
packages, including `rustypot`. Piper TTS checks additionally need `piper-tts`,
`aplay`, and a local Piper voice model. Voice files are not tracked.

## Making changes

- Keep changes scoped to the request.
- Match the existing shell/Python style.
- Update `README.md` when behavior, requirements, supported letters, safety,
  or known limitations change.
- Do not commit secrets, tokens, private keys, Piper voice files, logs with
  sensitive data, or machine-specific serial paths unless explicitly needed.
- Do not claim hardware testing unless you actually tested on the required
  hardware. Say what you tested and what you did not test.
- For pose accuracy, measure real offsets with `get_zeros`; `MIDDLE_POS` is a
  placeholder, and clamping is expected until calibrated.
- Supported-letter claims must match `make-gest.py`; remember `I`, `J`, `Y` are
  omitted and some poses are aliases or approximations.

## License

Contributions are accepted under the repository's MIT License in `LICENSE`.
