# Plan: Linux Clock Sync + Timezone Detection (Devuan/SysVinit)

## Overview
A boot-time script that force-syncs the system clock and auto-detects timezone
via layered detection. Includes a `tz` helper command with city name lookup,
timezone search, and cruise itinerary scheduling.

## Detection Priority (at boot)
1. **Schedule** — check `/etc/tz-schedule` for today's entry (no network needed, perfect for cruises)
2. **GeoIP** — IP-based geolocation via worldtimeapi.org (before VPN connects)
3. **WiFi fallback** — alternate IP geolocation provider if primary fails
4. **Manual** — use `tz` command as last resort

## Files

### 1. `sync-clock.sh` — Boot-time sync script
- Layered timezone detection (schedule -> GeoIP -> WiFi)
- Echo status to screen with 3-second delay
- Force-sync clock using `ntpd -g -q`
- Sync hardware clock with `hwclock --systohc`

### 2. `sync-clock` — SysVinit init.d script
- LSB headers with `Required-Start: $network $remote_fs`
- Runs before WireGuard comes up

### 3. `tz` — Timezone helper command
- `tz <city>` — set timezone by city name (e.g. `tz tampa`)
- `tz <timezone>` — set by timezone name (e.g. `tz America/Denver`)
- `tz list <keyword>` — search cities and timezones
- `tz schedule` — show cruise/travel itinerary
- `tz schedule add <date> <city> [note]` — add scheduled change
- `tz schedule clear` — clear schedule
- `tz schedule check` — apply today's entry (used by boot script)
- No arguments = show current timezone + next scheduled change

### 4. `tz-cities` — City-to-timezone mapping
- 150+ cities covering US, Caribbean, Mexico, Mediterranean, Europe, Asia, Pacific
- Focus on cruise ports and common travel destinations
- User-extensible (add entries at the bottom)

### 5. `README.md` — Installation and usage instructions
