#!/bin/bash
set -euo pipefail

# Prevent concurrent runs (boot + wake can race)
exec 9>/var/run/tz.lock
flock -n 9 || { logger "sync-clock: already running, skipping"; exit 0; }

GEO_URL="https://worldtimeapi.org/api/ip"
GEO_FALLBACK_URL="https://ipapi.co/timezone"
GEO_CACHE="/var/cache/tz/geoip"
GEO_CACHE_TTL=21600  # 6 hours in seconds

# --- Timezone Detection Functions ---

detect_tz_schedule() {
    # Method 0: Check pre-loaded schedule (e.g. cruise itinerary)
    /usr/local/bin/tz schedule check --query 2>/dev/null
}

check_geoip_cache() {
    if [ -f "$GEO_CACHE" ]; then
        local cached_time cached_tz now elapsed
        cached_time=$(head -1 "$GEO_CACHE")
        cached_tz=$(tail -1 "$GEO_CACHE")
        now=$(date +%s)
        elapsed=$((now - cached_time))
        if [ "$elapsed" -lt "$GEO_CACHE_TTL" ] && [ -f "/usr/share/zoneinfo/$cached_tz" ]; then
            echo "$cached_tz"
            return 0
        fi
    fi
    return 1
}

save_geoip_cache() {
    mkdir -p "$(dirname "$GEO_CACHE")"
    printf '%s\n%s\n' "$(date +%s)" "$1" > "$GEO_CACHE"
}

detect_tz_geoip() {
    # Check cache first
    local cached
    if cached=$(check_geoip_cache); then
        echo "$cached"
        return 0
    fi
    # Method 1: IP-based geolocation (fast, works before VPN)
    local result
    result=$(curl -s --max-time 5 "$GEO_URL" | grep -oP '"timezone"\s*:\s*"\K[^"]+')
    if [ -n "$result" ]; then
        save_geoip_cache "$result"
        echo "$result"
        return 0
    fi
    return 1
}

detect_tz_geoip_fallback() {
    # Method 2: Alternate GeoIP provider as second opinion
    local result
    result=$(curl -s --max-time 5 "$GEO_FALLBACK_URL")
    if [ -n "$result" ] && [ -f "/usr/share/zoneinfo/$result" ]; then
        save_geoip_cache "$result"
        echo "$result"
        return 0
    fi
    return 1
}

tz_offset_hours() {
    # Get UTC offset in hours for a given IANA timezone
    local zone="$1"
    TZ="$zone" date +%z 2>/dev/null | awk '{
        h = substr($0,1,3) + 0
        m = substr($0,4,2) + 0
        printf "%.1f", h + m/60
    }'
}

check_tz_confidence() {
    # Reject GeoIP results that jump >13 hours from current timezone.
    # Schedule and manual methods bypass this check.
    local new_tz="$1" method="$2"
    case "$method" in
        schedule|manual) return 0 ;;  # trusted sources, always accept
    esac

    local current_tz
    current_tz=$(cat /etc/timezone 2>/dev/null || echo "")
    [ -z "$current_tz" ] && return 0  # no baseline, accept anything

    local cur_off new_off diff
    cur_off=$(tz_offset_hours "$current_tz")
    new_off=$(tz_offset_hours "$new_tz")
    diff=$(awk "BEGIN { d=$new_off - $cur_off; print (d<0 ? -d : d) }")

    if awk "BEGIN { exit !($diff > 13) }"; then
        logger "sync-clock: rejecting $new_tz via $method — offset jump ${diff}h from $current_tz"
        echo "  Low confidence: $new_tz is ${diff}h from $current_tz, ignoring"
        return 1
    fi
    return 0
}

set_timezone() {
    local TZ="$1"
    local METHOD="$2"

    if [ ! -f "/usr/share/zoneinfo/$TZ" ]; then
        logger "sync-clock: detected timezone $TZ not found in zoneinfo, skipping"
        echo "  Warning: timezone '$TZ' not recognized, skipping"
        return 1
    fi

    if ! check_tz_confidence "$TZ" "$METHOD"; then
        return 1
    fi

    CURRENT_TZ=$(cat /etc/timezone 2>/dev/null || echo "")

    if [ "$TZ" != "$CURRENT_TZ" ]; then
        echo "$TZ" > /etc/timezone
        ln -sf "/usr/share/zoneinfo/$TZ" /etc/localtime
        export TZ="$TZ"
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

# Priority 3: GeoIP fallback (alternate provider)
if [ "$TZ_SET" = false ]; then
    logger "sync-clock: primary GeoIP failed, trying fallback"
    echo "  Primary GeoIP failed, trying fallback..."
    if TZ=$(detect_tz_geoip_fallback) && [ -n "$TZ" ]; then
        if set_timezone "$TZ" "GeoIP-fallback"; then
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

# --- Force NTP Sync (with retry) ---
echo ""
echo "Syncing clock..."
logger "sync-clock: starting NTP sync"

NTP_OK=false
for attempt in 1 2 3; do
    if ntpd -g -q; then
        NTP_OK=true
        break
    fi
    if [ "$attempt" -lt 3 ]; then
        logger "sync-clock: ntpd attempt $attempt failed, retrying in ${attempt}s..."
        echo "  Attempt $attempt failed, retrying..."
        sleep "$attempt"
    fi
done

if [ "$NTP_OK" = true ]; then
    hwclock --systohc
    logger "sync-clock: clock synchronized successfully"
    echo "  Clock synchronized: $(date)"
else
    logger "sync-clock: ntpd sync failed after 3 attempts"
    echo "  Clock sync failed after 3 attempts!"
    sleep 3
    exit 1
fi

echo ""
echo "=== Done ==="
sleep 3
