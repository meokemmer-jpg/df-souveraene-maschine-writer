#!/bin/bash
# K16 Concurrent-Spawn-Mutex Wrapper [CRUX-MK]
set -e
LOCK_DIR="/tmp/df-souveraene-maschine-writer.lock"
LOCK_AGE_LIMIT_S=21600
if [ -d "$LOCK_DIR" ]; then
  if [ "$(uname)" = "Darwin" ]; then
    LOCK_MTIME=$(stat -f %m "$LOCK_DIR" 2>/dev/null || echo 0)
  else
    LOCK_MTIME=$(stat -c %Y "$LOCK_DIR" 2>/dev/null || echo 0)
  fi
  LOCK_AGE_S=$(( $(date +%s) - LOCK_MTIME ))
  [ "$LOCK_AGE_S" -gt "$LOCK_AGE_LIMIT_S" ] && rm -rf "$LOCK_DIR"
fi
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "Lock exists - K16-VETO. Exiting."
  exit 3
fi
echo "$$" > "$LOCK_DIR/pid"
trap 'rm -rf "$LOCK_DIR"' EXIT INT TERM
cd "/Users/make/Projects/dark-factories/df-souveraene-maschine-writer"
python3 -m src.all_modules
exit $?
