#!/bin/bash
set -euo pipefail

GEO_URL="https://worldtimeapi.org/api/ip"
WIFI_IFACE="wlan0"

# --- Timezone Detection Functions ---

detect_tz_schedule() {
    # Method 0: Check pre-loaded schedule (e.g. cruise itinerary)
    /usr/local/bin/tz schedule check 2>/dev/null
}

detect_tz_geoip() {
    # Method 1: IP-based geolocation (fast, works before VPN)
    curl -s --max-time 5 "$GEO_URL" | grep -oP '"timezone"\s*:\s*"\K[^"]+'
}

detect_tz_wifi() {
    # Method 2: WiFi BSSID scan -> alternate IP geolocation provider
    local wifi_json

    # Get BSSIDs and signal levels from nearby WiFi networks
    wifi_json=$(iw dev "$WIFI_IFACE" scan 2>/dev/null | awk '
        /^BSS / { mac = $2; sub(/:?$/, "", mac) }
        /signal:/ { signal = $2; printf "{\"macAddress\":\"%s\",\"signalStrength\":%s}\n", mac, signal }
    ' | head -5)

    if [ -z "$wifi_json" ]; then
        return 1
    fi

    # WiFi-based services (Mozilla Location) are discontinued,
    # so we use a different IP geolocation provider as second opinion
    curl -s --max-time 5 "https://ipapi.co/timezone"
}

set_timezone() {
    local TZ="$1"
    local METHOD="$2"

    if [ ! -f "/usr/share/zoneinfo/$TZ" ]; then
        logger "sync-clock: detected timezone $TZ not found in zoneinfo, skipping"
        echo "  Warning: timezone '$TZ' not recognized, skipping"
        return 1
    fi

    CURRENT_TZ=$(cat /etc/timezone 2>/dev/null || echo "")

    if [ "$TZ" != "$CURRENT_TZ" ]; then
        echo "$TZ" > /etc/timezone
        ln -sf "/usr/share/zoneinfo/$TZ" /etc/localtime
        logger "sync-clock: timezone changed from $CURRENT_TZ to $TZ (via $METHOD)"
        echo "  Timezone updated: $CURRENT_TZ -> $TZ (via $METHOD)"
    else
        logger "sync-clock: timezone already set to $TZ"
        echo "  Timezone: $TZ (no change)"
    fi
    return 0
}

# --- Timezone Detection (layered, best-effort) ---
echo "=== Clock Sync ==="
echo ""
echo "Detecting timezone..."
logger "sync-clock: starting timezone detection"

TZ_SET=false

# Priority 1: Check schedule (cruise itinerary, no network needed)
if TZ=$(detect_tz_schedule) && [ -n "$TZ" ]; then
    if set_timezone "$TZ" "schedule"; then
        TZ_SET=true
    fi
fi

# Priority 2: GeoIP (before VPN connects)
if [ "$TZ_SET" = false ]; then
    if TZ=$(detect_tz_geoip) && [ -n "$TZ" ]; then
        if set_timezone "$TZ" "GeoIP"; then
            TZ_SET=true
        fi
    fi
fi

# Priority 3: WiFi-based fallback
if [ "$TZ_SET" = false ]; then
    logger "sync-clock: GeoIP failed, trying WiFi detection"
    echo "  GeoIP failed, trying WiFi scan..."
    if TZ=$(detect_tz_wifi) && [ -n "$TZ" ]; then
        if set_timezone "$TZ" "WiFi"; then
            TZ_SET=true
        fi
    fi
fi

if [ "$TZ_SET" = false ]; then
    CURRENT_TZ=$(cat /etc/timezone 2>/dev/null || echo "unknown")
    logger "sync-clock: all timezone detection failed, keeping $CURRENT_TZ"
    echo "  Detection failed, keeping current timezone: $CURRENT_TZ"
    echo "  (Use 'tz' command to set manually, e.g.: tz tampa)"
fi

# --- Force NTP Sync ---
echo ""
echo "Syncing clock..."
logger "sync-clock: starting NTP sync"
if ntpd -g -q; then
    hwclock --systohc
    logger "sync-clock: clock synchronized successfully"
    echo "  Clock synchronized: $(date)"
else
    logger "sync-clock: ntpd sync failed"
    echo "  Clock sync failed!"
    sleep 3
    exit 1
fi

echo ""
echo "=== Done ==="
sleep 3
