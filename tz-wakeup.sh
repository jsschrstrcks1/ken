#!/bin/sh
# Runs sync-clock.sh on laptop wake, but not more than once per 30 minutes

LASTSYNC="/var/run/last-clock-sync"
MIN_INTERVAL=1800

if [ -f "$LASTSYNC" ]; then
    last=$(cat "$LASTSYNC")
    now=$(date +%s)
    elapsed=$((now - last))
    if [ "$elapsed" -lt "$MIN_INTERVAL" ]; then
        logger "tz-wakeup: skipping sync (last sync ${elapsed}s ago)"
        exit 0
    fi
fi

logger "tz-wakeup: system resume detected, running clock sync"
/usr/local/bin/sync-clock.sh

date +%s > "$LASTSYNC"
