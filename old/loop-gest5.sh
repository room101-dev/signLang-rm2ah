#signLang-rm2ah/gest-loop5.sh
#!/usr/bin/env bash
# gest-loop5.sh -- gesture first, hold, ask, then wait before the next letter.
#
#   ./gest-loop5.sh              # A-Z every pass, identical each pass
#   ./gest-loop5.sh --random     # shuffled each pass
#   ./gest-loop5.sh --once       # one pass, exit
#   ./gest-loop5.sh --hint       # append "This is letter X." to the question
#   ./gest-loop5.sh -v           # 8-servo matrix + bus readback for every letter
#   ./gest-loop5.sh a b c        # explicit list
#   ./gest-loop5.sh --speed 4 --hold 2 --gap 8
#
# Per letter: make the gesture, hold --hold, speak the question (label
# appended when --hint), then wait --gap.
# Ctrl-C kills the in-flight child, opens the hand, exits 130.

set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GEST="$HERE/make-gest2.py"
SAY="$HERE/say.py"
PY="${PY:-python3}"
PROMPT="${PROMPT:-reach-ee mini, what do you see? What letter is this hand gesture?}"

SPEED=4
HOLD=2
GAP=8
RANDOM_ORDER=0
ONCE=0
HINT=0
VERBOSE=0
EXPLICIT=()

# A-Z, identical every pass.  I, J, Y need a pinky.
DEFAULT_ORDER=(A B C D E F G H K L M N O P Q R S T U V W X Z)

LOG="${LOG:-$HERE/logs/gest-$(date +%Y%m%d-%H%M%S).log}"
mkdir -p "$(dirname "$LOG")"
log() { printf '%s %s\n' "$(date +%H:%M:%S)" "$*" | tee -a "$LOG"; }

usage() { sed -n '2,16p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --random|-r)  RANDOM_ORDER=1 ;;
    --once|-1)    ONCE=1 ;;
    --hint|-H)    HINT=1 ;;
    -v|--verbose) VERBOSE=1 ;;
    --speed)      SPEED="$2"; shift ;;
    --hold)       HOLD="$2"; shift ;;
    --gap)        GAP="$2"; shift ;;
    --prompt)     PROMPT="$2"; shift ;;
    -h|--help)    usage; exit 0 ;;
    -*)           echo "unknown option $1" >&2; usage; exit 2 ;;
    *)            EXPLICIT+=("$1") ;;
  esac
  shift
done

[[ -x "$GEST" ]] || { echo "missing or not executable: $GEST" >&2; exit 1; }

GEST_ARGS=()
[[ $VERBOSE -eq 1 ]] && GEST_ARGS+=(-v)

CHILD=""
run() {
  "$@" &
  CHILD=$!
  wait "$CHILD"
  local rc=$?
  CHILD=""
  return $rc
}

say() {
  local msg="$*"
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
    pkill -TERM -P "$CHILD" 2>/dev/null
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

log "log: $LOG"
if [[ $VERBOSE -eq 1 ]]; then
  "$GEST" --list -v | tee -a "$LOG"
fi

pass=0
while :; do
  pass=$((pass + 1))
  if [[ $RANDOM_ORDER -eq 1 ]]; then
    mapfile -t RUN < <(printf '%s\n' "${ORDER[@]}" | shuf)
  else
    RUN=("${ORDER[@]}")
  fi

  log "=== pass $pass: ${#RUN[@]} letters ==="
  aborted=0
  for L in "${RUN[@]}"; do
    log "--> $L"
    run "$GEST" "${GEST_ARGS[@]}" "$L" --speed "$SPEED" --hold "$HOLD" \
      2>&1 | tee -a "$LOG"
    rc=${PIPESTATUS[0]}

    if [[ $rc -eq 3 ]]; then
      log "!! hand did not respond at $L -- aborting pass"
      aborted=1
      break
    elif [[ $rc -ne 0 ]]; then
      log "   (failed: $L, rc=$rc)"
    fi

    if [[ $HINT -eq 1 ]]; then
      say "$PROMPT This is letter $L."
      log "LABEL=$L"
    else
      say "$PROMPT"
    fi

    sleep "$GAP"
  done

  [[ $aborted -eq 1 ]] && break
  [[ $ONCE -eq 1 ]] && break
  log "--- pass $pass done, looping (Ctrl-C to stop) ---"
done
