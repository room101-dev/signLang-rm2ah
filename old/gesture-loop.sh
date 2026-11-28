#!/usr/bin/env bash
# gesture-loop.sh -- speak a prompt, make a letter, pause, next.
#
#   ./gesture-loop.sh                  # alphabetical, reads-well letters first
#   ./gesture-loop.sh --random         # shuffled, forever
#   ./gesture-loop.sh --once           # one pass, exit
#   ./gesture-loop.sh a b c            # explicit list
#   ./gesture-loop.sh --speed 3 --hold 2 --gap 6
#
# Run from the talk venv so say.py finds piper:
#   source ~/robot/talk/venv/bin/activate
#
# Sound driver is say.py next to this script (Piper), espeak fallback.

set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GEST="$HERE/make-gest.py"
SAY="$HERE/say.py"
PY="${PY:-python3}"
PROMPT="${PROMPT:-reachy mini, what do you see? What letter is this hand gesture?}"

SPEED=4
HOLD=1.5
GAP=6
RANDOM_ORDER=0
ONCE=0
EXPLICIT=()

# reads-well first, then thumb-dependent, then the shaky ones
DEFAULT_ORDER=(
  A G H K L U V W X Z
  B C E M N S T
  D F O
)

usage() { sed -n '2,13p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --random|-r) RANDOM_ORDER=1 ;;
    --once|-1)   ONCE=1 ;;
    --speed)     SPEED="$2"; shift ;;
    --hold)      HOLD="$2"; shift ;;
    --gap)       GAP="$2"; shift ;;
    --prompt)    PROMPT="$2"; shift ;;
    -h|--help)   usage; exit 0 ;;
    -*)          echo "unknown option $1" >&2; usage; exit 2 ;;
    *)           EXPLICIT+=("$1") ;;
  esac
  shift
done

[[ -x "$GEST" ]] || { echo "missing or not executable: $GEST" >&2; exit 1; }

say() {
  local msg="$1"
  if [[ -f "$SAY" ]]; then
    "$PY" "$SAY" --quiet "$msg"
  elif command -v espeak-ng >/dev/null 2>&1; then
    espeak-ng -v en -s 150 "$msg"
  elif command -v espeak >/dev/null 2>&1; then
    espeak -v en -s 150 "$msg"
  else
    echo "$msg"
  fi
}

open_hand() {
  "$GEST" open --speed 5 --hold 0.2 >/dev/null 2>&1 || true
}
trap open_hand EXIT INT TERM

if [[ ${#EXPLICIT[@]} -gt 0 ]]; then
  ORDER=("${EXPLICIT[@]}")
else
  ORDER=("${DEFAULT_ORDER[@]}")
fi

pass=0
while :; do
  pass=$((pass + 1))
  if [[ $RANDOM_ORDER -eq 1 ]]; then
    mapfile -t RUN < <(printf '%s\n' "${ORDER[@]}" | shuf)
  else
    RUN=("${ORDER[@]}")
  fi

  echo "=== pass $pass: ${#RUN[@]} letters ==="
  for L in "${RUN[@]}"; do
    say "$PROMPT"
    sleep 0.3
    echo "--> $L"
    "$GEST" "$L" --speed "$SPEED" --hold "$HOLD" || echo "  (failed: $L)"
    sleep "$GAP"
  done

  [[ $ONCE -eq 1 ]] && break
  echo "--- pass $pass done, looping (Ctrl-C to stop) ---"
done
