# Plan: Linux Clock Sync + Timezone Detection (Devuan/SysVinit)

## Overview
A boot-time script that force-syncs the system clock and auto-detects timezone
via layered detection. Includes a `tz` helper command with city name lookup
(1200+ cruise ports), timezone search, cruise itinerary scheduling, and
wake-from-sleep hooks.

## Detection Priority (at boot and wake)
1. **Schedule** — check `/etc/tz-schedule` for today's entry (no network needed)
2. **GeoIP** — IP-based geolocation via worldtimeapi.org (before VPN connects)
3. **GeoIP fallback** — ipapi.co as second provider if primary fails
4. **Manual** — use `tz` command as last resort

## Changes in this iteration

### 1. Remove WiFi detection, replace with simple GeoIP fallback
**File:** `sync-clock.sh`
- Delete `detect_tz_wifi()` entirely (WiFi BSSID scan + iw dependency is dead weight since Mozilla Location Services shut down)
- Replace with `detect_tz_geoip_fallback()` that just calls `ipapi.co/timezone`
- Detection chain becomes: schedule → worldtimeapi.org → ipapi.co → keep current
- Remove `iw` from dependencies in README

### 2. Fix double timezone application
**File:** `tz` (cmd_schedule check)
- Add `--query` flag to `tz schedule check`
- `tz schedule check` — applies timezone AND returns it (for manual use)
- `tz schedule check --query` — returns timezone only, no side effects
- **File:** `sync-clock.sh` — change `detect_tz_schedule()` to call `tz schedule check --query`

### 3. Auto-SEA inference in cruise mode
**File:** `tz` (cmd_cruise)
- When adding a port, compare its timezone to the previous port's timezone
- If timezones differ, auto-insert a SEA day before the new port
- Same port repeated = multi-day stay, no SEA inserted
- Same timezone but different port = direct sailing, no SEA inserted
- Different timezone = SEA day auto-inserted (timezone changes at ~2am on ships)
- Explicit `tz cruise sea` still works for multi-day crossings (transatlantic, Panama Canal, etc.)
- Show "(auto)" marker on auto-inserted SEA days to distinguish from manual ones

### 4. Move cruise state to /var/lib/tz/
**File:** `tz`
- Change `CRUISE_STATE` from `/tmp/tz-cruise-state` to `/var/lib/tz/cruise-state`
- Create `/var/lib/tz/` directory if it doesn't exist
- Survives reboots so you don't lose a half-built itinerary

### 5. Add `tz cruise load <file>`
**File:** `tz` (cmd_cruise)
- Load itinerary from a plain text file
- File format:
  ```
  2026-02-24
  cabo
  cabo
  ensenada
  los angeles
  tampa
  ```
  First line = start date, remaining lines = ports (or "sea" for explicit sea days)
- Resolves each port, applies auto-SEA inference, writes schedule
- Enables saving/reusing itineraries across trips
- Example: `tz cruise load ~/cruises/west-coast-2026.txt`

### 6. Add `tz here`
**File:** `tz`
- Detect timezone from network (GeoIP) and apply immediately
- Useful when landing somewhere without rebooting
- Tries worldtimeapi.org first, falls back to ipapi.co
- Shows result: `Detected: America/Denver (via GeoIP)`

### 7. Add `tz explain`
**File:** `tz`
- Show current timezone state with source information
- Output:
  ```
  Timezone:  America/Mazatlan
  Local time: 09:34 PST
  UTC offset: -07:00
  Schedule:  active (cruise itinerary)
  Today:     2026-02-26 — cabo san lucas
  Next:      2026-02-27 — SEA → America/Tijuana
  ```
- Makes debugging trivial

### 8. Update README.md
- Remove `iw` from dependencies
- Add `tz here`, `tz explain`, `tz cruise load` to usage docs
- Update detection priority description

### 9. Update plan.md
- Reflect new architecture

## Files

### 1. `sync-clock.sh` — Boot-time sync script
- Layered timezone detection (schedule → GeoIP → GeoIP fallback)
- Echo status to screen with 3-second delay
- NTP sync with retry logic (3 attempts)
- Sync hardware clock with `hwclock --systohc`

### 2. `sync-clock` — SysVinit init.d script
- LSB headers with `Required-Start: $network $remote_fs`
- Runs before WireGuard comes up

### 3. `tz` — Timezone helper command
- `tz` — show current timezone
- `tz <city>` — set timezone by city name
- `tz here` — detect from network and set
- `tz explain` — show timezone state + source info
- `tz list <keyword>` — search cities and timezones
- `tz undo` — remove last schedule entry
- `tz schedule` — manage schedule entries
- `tz cruise start <date>` — start building cruise itinerary
- `tz cruise <port>` — add next port (auto-SEA inference)
- `tz cruise sea` — explicit sea day (multi-day crossings)
- `tz cruise load <file>` — load itinerary from file
- `tz cruise end` — finish itinerary

### 4. `tz-cities` — City-to-timezone mapping
- 1200+ cruise ports from whatsinport.com
- Fuzzy matching (cabo, cabo-san-lucas, cabo san lucas all work)
- Grouped by region with comments

### 5. `tz-wakeup-event` + `tz-wakeup.sh` — ACPI wake hook
- Runs sync-clock.sh when laptop lid opens
- Throttled to max once per 30 minutes

### 6. `README.md` — Installation and usage instructions

## Dependencies
- curl
- ntpd
- logger (bsdutils)
- acpid (for wake hook)
- ~~iw~~ (removed — no longer needed)
