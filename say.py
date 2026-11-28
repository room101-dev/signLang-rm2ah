#!/usr/bin/env python3
"""
say.py -- Piper TTS only, stripped out of test-loop24.py.

One shot:
    python3 say.py "reachy mini what do you see? What letter is this hand gesture?"

Long lived (loads the voice once, then speaks each stdin line):
    python3 say.py
    echo "hello" | python3 say.py

Importable:
    from say import speak
    speak("hello")

Needs the same venv as test-loop24.py (piper + aplay on PATH).
Voice model resolution order: --model, $PIPER_MODEL, ./piper/<default>,
~/robot/talk/piper/<default>.
"""

import argparse
import os
import subprocess
import sys
import time

DEFAULT_VOICE = "en_US-lessac-medium.onnx"


def find_model(explicit=None):
    if explicit:
        return explicit if os.path.isfile(explicit) else None
    if os.environ.get("PIPER_MODEL"):
        return os.environ["PIPER_MODEL"]
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(os.getcwd(), "piper", DEFAULT_VOICE),
        os.path.join(here, "piper", DEFAULT_VOICE),
        os.path.expanduser(f"~/robot/talk/piper/{DEFAULT_VOICE}"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


def load_voice(model_path):
    """Import piper with ALSA/portaudio C-spam suppressed, then load."""
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    os.dup2(devnull, 2)
    try:
        from piper import PiperVoice
    finally:
        os.dup2(old_stderr, 2)
        os.close(devnull)
        os.close(old_stderr)
    return PiperVoice.load(model_path)


class Speaker:
    def __init__(self, model_path):
        self.voice = load_voice(model_path)
        self.sample_rate = self.voice.config.sample_rate

    def speak(self, text):
        if not text or not text.strip():
            return
        clean_text = text.strip().replace("\n", " ")
        try:
            # Direct aplay pipe -- keeps VirtIO/container audio clean
            aplay = subprocess.Popen(
                ["aplay", "-r", str(self.sample_rate), "-f", "S16_LE", "-c", "1", "-q"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            total_samples = 0
            for chunk in self.voice.synthesize(clean_text):
                aplay.stdin.write(chunk.audio_int16_bytes)
                total_samples += len(chunk.audio_int16_bytes) // 2

            aplay.stdin.close()
            aplay.wait()

            # drain whatever aplay still has buffered
            residual = max(0.25, (total_samples / float(self.sample_rate)) * 0.15)
            time.sleep(residual)
        except Exception as e:
            print(f"  [TTS Error]: {e}", file=sys.stderr)


_speaker = None


def speak(text):
    """Module-level convenience; loads the voice on first use."""
    global _speaker
    if _speaker is None:
        model = find_model()
        if not model:
            raise RuntimeError("piper voice model not found (set PIPER_MODEL)")
        _speaker = Speaker(model)
    _speaker.speak(text)


def main():
    ap = argparse.ArgumentParser(description="Piper TTS, one shot or stdin lines.")
    ap.add_argument("text", nargs="*", help="text to speak; omit to read stdin lines")
    ap.add_argument("--model", help="path to .onnx voice")
    ap.add_argument("--quiet", action="store_true", help="no per-line echo")
    args = ap.parse_args()

    model = find_model(args.model)
    if not model:
        print(f"error: piper voice not found. looked for ./piper/{DEFAULT_VOICE}, "
              f"~/robot/talk/piper/{DEFAULT_VOICE}. set PIPER_MODEL or --model.",
              file=sys.stderr)
        return 1
    if not os.path.isfile(model):
        print(f"error: no such model file: {model}", file=sys.stderr)
        return 1

    spk = Speaker(model)

    if args.text:
        line = " ".join(args.text)
        if not args.quiet:
            print(f"[say] {line}", flush=True)
        spk.speak(line)
        return 0

    # stdin mode: voice stays loaded
    if not args.quiet:
        print(f"[say] ready ({model}, {spk.sample_rate} Hz)", file=sys.stderr, flush=True)
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line.strip():
            continue
        if not args.quiet:
            print(f"[say] {line}", flush=True)
        spk.speak(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
