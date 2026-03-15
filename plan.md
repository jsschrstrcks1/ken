# Plan: Linux Clock Sync + Timezone Detection (Devuan/SysVinit)

## Overview
A boot-time script that force-syncs the system clock and auto-detects timezone
via layered detection (GeoIP -> WiFi scan fallback), before VPN starts.
Includes a manual `tz` helper command as a reliable last resort for travelers.
Outputs status to screen with a 3-second delay so you can see the result during boot.

## Files

### 1. `sync-clock.sh` — Boot-time sync script
- **Layer 1:** Detect timezone via GeoIP (https://worldtimeapi.org/api/ip)
- **Layer 2:** If GeoIP fails, scan WiFi BSSIDs via `iw` and try alternate IP geolocation
- Fail safely if both fail (log and continue with current timezone)
- Write to `/etc/timezone` and symlink `/etc/localtime` (no timedatectl)
- Force-sync clock using `ntpd -g -q`
- Sync hardware clock with `hwclock --systohc`
- Echo timezone and clock status to screen with 3-second delay
- Uses `set -euo pipefail` and `logger` throughout

### 2. `sync-clock` — SysVinit init.d script
- LSB headers with `Required-Start: $network $remote_fs`
- Runs before WireGuard comes up
- Only implements `start`

### 3. `tz` — Manual timezone helper command
- Usage: `tz America/Denver`, `tz Europe/London`
- Validates timezone exists in `/usr/share/zoneinfo/`
- Updates `/etc/timezone` and `/etc/localtime` symlink
- Shows current date/time after change
- No arguments = show current timezone

### 4. `README.md` — Installation instructions
- Copy scripts to `/usr/local/bin/`, make executable
- Copy init.d script, register with `update-rc.d`
- Dependencies: curl, ntpd, iw, logger
