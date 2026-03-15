#!/bin/bash
set -euo pipefail

GEO_URL="https://worldtimeapi.org/api/ip"

# --- Timezone Detection (best-effort, before VPN) ---
logger "sync-clock: starting timezone detection"
if TZ=$(curl -s --max-time 5 "$GEO_URL" | grep -oP '"timezone"\s*:\s*"\K[^"]+'); then
    if [ -f "/usr/share/zoneinfo/$TZ" ]; then
        CURRENT_TZ=$(cat /etc/timezone 2>/dev/null || echo "")
        if [ "$TZ" != "$CURRENT_TZ" ]; then
            echo "$TZ" > /etc/timezone
            ln -sf "/usr/share/zoneinfo/$TZ" /etc/localtime
            logger "sync-clock: timezone changed from $CURRENT_TZ to $TZ"
        else
            logger "sync-clock: timezone already set to $TZ"
        fi
    else
        logger "sync-clock: detected timezone $TZ not found in zoneinfo, skipping"
    fi
else
    logger "sync-clock: GeoIP detection failed, keeping current timezone"
fi

# --- Force NTP Sync ---
logger "sync-clock: starting NTP sync"
if ntpd -g -q; then
    hwclock --systohc
    logger "sync-clock: clock synchronized successfully"
else
    logger "sync-clock: ntpd sync failed"
    exit 1
fi
