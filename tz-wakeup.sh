#!/bin/sh
# Runs sync-clock.sh on laptop wake, but not more than once per 30 minutes

# Prevent concurrent runs
exec 9>/var/run/tz-wakeup.lock
flock -n 9 || exit 0

LASTSYNC="/var/run/last-clock-sync"
MIN_INTERVAL=1800

if [ -f "$LASTSYNC" ]; then
    last=$(cat "$LASTSYNC")
    case "$last" in *[!0-9]*) last=0 ;; esac
    now=$(date +%s)
    elapsed=$((now - last))
    if [ "$elapsed" -lt "$MIN_INTERVAL" ]; then
        logger "tz-wakeup: skipping sync (last sync ${elapsed}s ago)"
        exit 0
    fi
fi

logger "tz-wakeup: system resume detected, running clock sync"
/usr/local/bin/sync-clock.sh

# Atomic write to prevent symlink attacks
date +%s > "${LASTSYNC}.tmp" && mv "${LASTSYNC}.tmp" "$LASTSYNC"
