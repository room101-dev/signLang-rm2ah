#!/usr/bin/env bash
# gest-loop2.sh -- speak a prompt, make a letter, let the RM answer, correct it.
#
#   ./gest-loop2.sh                # alphabetical, reads-well letters first
#   ./gest-loop2.sh --random       # shuffled each pass
#   ./gest-loop2.sh --once         # one pass, exit
#   ./gest-loop2.sh --hint         # after the gap, say "This is letter X."
#   ./gest-loop2.sh a b c          # explicit list
#   ./gest-loop2.sh --speed 3 --hold 2 --gap 7
#
# Ctrl-C kills the in-flight child, opens the hand, exits 130.

set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GEST="$HERE/make-gest.py"
SAY="$HERE/say.py"
PY="${PY:-python}"
PROMPT="${PROMPT:-reach-ee mini, what do you see? What letter is this hand gesture?}"

SPEED=4
HOLD=1.5
GAP=6
RANDOM_ORDER=0
ONCE=0
HINT=0
EXPLICIT=()

DEFAULT_ORDER=(
  A G H K L U V W X Z
  B C E M N S T
  D F O
)

usage() { sed -n '2,11p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --random|-r) RANDOM_ORDER=1 ;;
    --once|-1)   ONCE=1 ;;
    --hint|-H)   HINT=1 ;;
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

CHILD=""
run() {                       # background + wait so SIGINT can kill it
  "$@" &
  CHILD=$!
  wait "$CHILD"
  local rc=$?
  CHILD=""
  return $rc
}

say() {
  local msg="$1"
  if [[ -f "$SAY" ]]; then
    run "$PY" "$SAY" --quiet "$msg"
  elif command -v espeak-ng >/dev/null 2>&1; then
    run espeak-ng -v en -s 150 "$msg"
  elif command -v espeak >/dev/null 2>&1; then
    run espeak -v en -s 150 "$msg"
  else
    echo "$msg"
  fi
}

open_hand() {
  "$GEST" open --speed 5 --hold 0.2 >/dev/null 2>&1 || true
}

cleanup() {
  if [[ -n "$CHILD" ]]; then
    pkill -TERM -P "$CHILD" 2>/dev/null   # aplay under say.py
    kill -TERM "$CHILD" 2>/dev/null
    wait "$CHILD" 2>/dev/null
    CHILD=""
  fi
  open_hand
}
trap cleanup EXIT
trap 'echo; exit 130' INT TERM

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
    run "$GEST" "$L" --speed "$SPEED" --hold "$HOLD" || echo "  (failed: $L)"
    sleep "$GAP"
    if [[ $HINT -eq 1 ]]; then
      say "This is letter $L."
      echo "LABEL=$L"
    fi
  done

  [[ $ONCE -eq 1 ]] && break
  echo "--- pass $pass done, looping (Ctrl-C to stop) ---"
done
