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

## Current Architecture

### Detection chain (boot, wake, network change)
1. **Schedule** — `/etc/tz-schedule` for today's entry (no network needed)
2. **GeoIP** — worldtimeapi.org with 6-hour cache
3. **GeoIP fallback** — ipapi.co as second provider
4. **Manual** — `tz` command

### Triggers
- **Boot**: SysVinit service (`/etc/init.d/sync-clock`)
- **Wake**: ACPI hook (`/etc/acpi/tz-wakeup.sh`), throttled to 30min
- **Network change**: if-up.d hook (`tz-network-check`), throttled to 5min

### Security hardening (latest iteration)
- Timezone string validation: `^[A-Za-z0-9_/+-]+$`, no `..` (blocks path traversal via GeoIP responses)
- Atomic state file writes (temp + mv) to prevent symlink attacks
- State directories 0700 root:root
- flock on all entry points (sync-clock.sh, tz-network-check, tz-wakeup.sh)
- SSID sanitization: non-printable chars stripped, 32-byte limit
- AWK variables via `-v` flag (no string interpolation injection)
- grep -F for user input (no regex injection)
- grep -Fxv replaces sed with user-controlled delimiters
- curl --fail rejects HTML error pages as timezone data
- Numeric validation on cooldown/timestamp files
- install(1) with explicit ownership instead of cp+chmod

## Files

### 1. `sync-clock.sh` — Boot/wake sync script
- Layered timezone detection (schedule → GeoIP → GeoIP fallback)
- Timezone validation (path traversal, character whitelist)
- GeoIP cache with 6-hour TTL, atomic writes
- Confidence check rejects >13h timezone jumps from GeoIP
- NTP sync with retry logic (3 attempts)
- Sync hardware clock with `hwclock --systohc`
- flock prevents concurrent runs

### 2. `sync-clock` — SysVinit init.d script
- LSB headers with `Required-Start: $network $remote_fs`
- Runs before WireGuard comes up

### 3. `tz` — Timezone helper command
- `tz` — dashboard (status, trip info, next change)
- `tz <city>` — set timezone by city name (or add to trip)
- `tz here` — detect from network and set
- `tz list <keyword>` — search cities and timezones (fixed-string match)
- `tz undo` — remove last schedule entry (safe string matching)
- `tz schedule` — manage schedule entries
- `tz trip start <date> <city>` — start building trip itinerary
- `tz trip load <file>` — load itinerary from file
- `tz trip end` — finish itinerary
- `tz sea` — explicit sea day
- `tz +<city>` — same-day port
- Timezone validation on all input paths

### 4. `tz-cities` — City-to-timezone mapping
- 1200+ cruise ports
- Fuzzy matching (cabo, cabo-san-lucas, cabo san lucas all work)
- Grouped by region with comments

### 5. `tz-wakeup-event` + `tz-wakeup.sh` — ACPI wake hook
- Runs sync-clock.sh when laptop lid opens
- Throttled to max once per 30 minutes
- flock prevents concurrent runs
- Atomic state file writes

### 6. `tz-network-check` — Network change hook
- Triggers on interface up via if-up.d
- Detects SSID + gateway changes
- SSID sanitized (printable chars only, 32-byte limit)
- Throttled to once per 5 minutes
- flock prevents concurrent runs
- Atomic state file writes

### 7. `install.sh` — Installation script
- Uses install(1) with explicit ownership (root:root)
- State directories set to 0700

## Dependencies
- curl
- ntpd (ntp package)
- logger (bsdutils)
- acpid (optional, for wake hook)
- wireless-tools (optional, for iwgetid in network change detection)
