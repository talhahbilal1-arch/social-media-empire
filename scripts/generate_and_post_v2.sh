#!/bin/bash
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
cd "$HOME/Desktop/social-media-empire" || exit 1
LOGDIR="$PWD/logs"
mkdir -p "$LOGDIR"
DATE=$(date +%Y%m%d_%H%M%S)
LOG="$LOGDIR/run_${DATE}.log"
echo "=== Video Generation Run: $(date) ===" >> "$LOG"
SUCCESS=0
FAIL=0
for brand in fitover35 deals menopause; do
  echo "--- [$brand] Starting $(date +%H:%M:%S) ---" >> "$LOG"
  python3 -m video_pipeline.generate --brand "$brand" --format pinterest --count 1 >> "$LOG" 2>&1
  EC=$?
  if [ $EC -eq 0 ]; then
    echo "--- [$brand] SUCCESS (exit $EC) ---" >> "$LOG"
    SUCCESS=$((SUCCESS + 1))
  else
    echo "--- [$brand] FAILED (exit $EC) ---" >> "$LOG"
    FAIL=$((FAIL + 1))
  fi
  sleep 5
done
echo "=== Results: $SUCCESS succeeded, $FAIL failed ===" >> "$LOG"
echo "=== Run Complete: $(date) ===" >> "$LOG"
find "$LOGDIR" -name "run_*.log" -mtime +30 -delete 2>/dev/null
