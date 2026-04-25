#!/usr/bin/env bash
# Install the launchd agent that runs local_video_pipeline.py every 8 hours.
#
# Idempotent: unloads any previous version before loading the new one, so
# you can re-run this after editing the plist. The script itself reads
# .env at runtime — no secrets are embedded in the plist.
#
# Usage:
#   bash scripts/install_video_pipeline.sh         # install / refresh
#   bash scripts/install_video_pipeline.sh remove  # uninstall

set -euo pipefail

REPO=/Users/homefolder/Desktop/social-media-empire
PLIST_NAME=com.socialmediaempire.videopipeline.plist
SRC=$REPO/scripts/$PLIST_NAME
DEST=$HOME/Library/LaunchAgents/$PLIST_NAME

mode=${1:-install}

case "$mode" in
    install)
        if [[ ! -f $SRC ]]; then
            echo "plist not found at $SRC" >&2
            exit 1
        fi
        mkdir -p "$REPO/logs"
        cp "$SRC" "$DEST"
        # unload first (ignore failure — it's fine if nothing was loaded)
        launchctl unload "$DEST" 2>/dev/null || true
        launchctl load "$DEST"
        echo "loaded: $DEST"
        echo "logs:   $REPO/logs/video_pipeline.log"
        echo "trigger now: launchctl start com.socialmediaempire.videopipeline"
        ;;
    remove|uninstall)
        launchctl unload "$DEST" 2>/dev/null || true
        rm -f "$DEST"
        echo "removed: $DEST"
        ;;
    *)
        echo "usage: $0 [install|remove]" >&2
        exit 2
        ;;
esac
