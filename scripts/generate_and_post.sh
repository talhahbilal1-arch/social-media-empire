#!/bin/bash
# generate_and_post.sh — Standalone Mac video pipeline (runs without Claude)
# Triggered by launchd 3x daily (9AM / 2PM / 7PM)
# NOTE: A Claude scheduled task "daily-video-generation" may also exist — disable it
#       if you want launchd to be the sole trigger (avoids double-posting).

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

# Always run from main project root (not a worktree)
PROJECT_DIR="$HOME/Desktop/social-media-empire"
cd "$PROJECT_DIR" || { echo "ERROR: Cannot cd to $PROJECT_DIR"; exit 1; }

LOGDIR="$PROJECT_DIR/logs"
mkdir -p "$LOGDIR"

DATE=$(date +%Y%m%d_%H%M%S)
LOG="$LOGDIR/run_${DATE}.log"

echo "=== Video Generation Run: $(date) ===" >> "$LOG"
echo "Project: $PROJECT_DIR" >> "$LOG"
echo "Python: $(which python3)" >> "$LOG"
echo "" >> "$LOG"

# Brand keys must match video_pipeline/config.py BRANDS dict
for brand in fitover35 deals menopause; do
  echo "--- Starting $brand ---" >> "$LOG"
  python3 -m video_pipeline.generate --brand "$brand" --format pinterest --count 1 >> "$LOG" 2>&1
  EXIT_CODE=$?
  echo "--- $brand done (exit code: $EXIT_CODE) ---" >> "$LOG"
  echo "" >> "$LOG"
  sleep 5
done

echo "=== Run Complete: $(date) ===" >> "$LOG"

# Keep logs for 30 days, then auto-delete
find "$LOGDIR" -name "run_*.log" -mtime +30 -delete
