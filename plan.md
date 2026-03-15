# Plan: Linux Clock Sync + Timezone Detection (Devuan/SysVinit)

## Overview
A boot-time script that force-syncs the system clock and auto-detects timezone
via GeoIP (best-effort, before VPN starts). Includes a manual `tz` helper
command as a reliable fallback for travelers.

## Files to create

### 1. `sync-clock.sh` — Boot-time sync script
- Detect timezone via GeoIP (https://worldtimeapi.org/api/ip)
- Write to `/etc/timezone` and symlink `/etc/localtime` (no timedatectl)
- Fail safely if detection fails (log and continue)
- Force-sync clock using `ntpd -g -q`
- Sync hardware clock with `hwclock --systohc`
- Uses `set -euo pipefail` and `logger` throughout

### 2. `sync-clock` — SysVinit init.d script
- LSB headers with `Required-Start: $network $remote_fs`
- Runs before WireGuard comes up
- `Type: oneshot` equivalent — only implements `start`

### 3. `tz` — Manual timezone helper command
- Usage: `tz America/Denver`, `tz Europe/London`
- Validates timezone exists in `/usr/share/zoneinfo/`
- Updates `/etc/timezone` and `/etc/localtime` symlink
- Shows current date/time after change
- No arguments = show current timezone

### 4. `README.md` — Installation instructions
- Copy scripts to `/usr/local/bin/`, make executable
- Copy init.d script, register with `update-rc.d`
- Dependencies: curl, ntpd, logger

## Implementation steps
1. Create `sync-clock.sh`
2. Create `sync-clock` init.d script
3. Create `tz` helper command
4. Create `README.md`
5. Commit and push to branch
