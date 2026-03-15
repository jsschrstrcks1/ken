# Plan: Linux Clock Sync + Timezone Detection (Devuan/SysVinit)

## Overview
A boot-time script that force-syncs the system clock and auto-detects timezone
via layered detection. Includes a `tz` helper command with city name lookup
(1200+ cruise ports), timezone search, cruise itinerary scheduling, and
wake-from-sleep hooks.

## Detection Priority (at boot and wake)
1. **Schedule** — check `/etc/tz-schedule` for today's entry (no network needed)
2. **GeoIP** — IP-based geolocation via worldtimeapi.org (before VPN connects)
3. **WiFi fallback** — alternate IP geolocation provider if primary fails
4. **Manual** — use `tz` command as last resort

## Files

### 1. `sync-clock.sh` — Boot-time sync script
- Layered timezone detection (schedule -> GeoIP -> WiFi)
- Echo status to screen with 3-second delay
- NTP sync with retry logic (3 attempts)
- Sync hardware clock with `hwclock --systohc`

### 2. `sync-clock` — SysVinit init.d script
- LSB headers with `Required-Start: $network $remote_fs`
- Runs before WireGuard comes up

### 3. `tz` — Timezone helper command
- `tz <city>` — set timezone by city name
- `tz list <keyword>` — search cities and timezones
- `tz undo` — remove last schedule entry
- `tz schedule` — manage schedule entries
- `tz cruise start <date>` — start building cruise itinerary
- `tz cruise <port>` — add next port (auto-increments date)
- `tz cruise sea` — add a sea day
- `tz cruise end` — finish itinerary

### 4. `tz-cities` — City-to-timezone mapping
- 1200+ cruise ports from whatsinport.com
- Fuzzy matching (cabo, cabo-san-lucas, cabo san lucas all work)
- Grouped by region with comments

### 5. `tz-wakeup-event` + `tz-wakeup.sh` — ACPI wake hook
- Runs sync-clock.sh when laptop lid opens
- Throttled to max once per 30 minutes

### 6. `README.md` — Installation and usage instructions
