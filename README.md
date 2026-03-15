# Clock Sync + Timezone Detection (Devuan/SysVinit)

Automatically syncs the system clock and detects timezone at boot.
Includes a manual `tz` command for reliable timezone changes when traveling.

## What it does

### At boot (`sync-clock.sh`)
1. Detects timezone via IP geolocation (before VPN connects)
2. If GeoIP fails, falls back to WiFi-based detection
3. Updates `/etc/timezone` and `/etc/localtime` if timezone changed
4. Force-syncs the clock using `ntpd -g -q` (allows large time jumps)
5. Writes corrected time to the hardware clock
6. Displays results on screen for 3 seconds

If all automatic detection fails, the current timezone is kept.
Use the `tz` command to set it manually.

### Manual timezone change (`tz`)
```
tz America/Denver
tz Europe/London
tz                    # show current timezone
```

## Dependencies
- curl
- ntpd
- iw (for WiFi fallback)
- logger (bsdutils)

## Installation

1. Copy scripts and make them executable:
```
sudo cp sync-clock.sh /usr/local/bin/sync-clock.sh
sudo cp tz /usr/local/bin/tz
sudo chmod +x /usr/local/bin/sync-clock.sh /usr/local/bin/tz
```

2. Install the init.d service:
```
sudo cp sync-clock /etc/init.d/sync-clock
sudo chmod +x /etc/init.d/sync-clock
sudo update-rc.d sync-clock defaults
```

3. (Optional) Test it now:
```
sudo /etc/init.d/sync-clock start
```

## Boot output example
```
=== Clock Sync ===

Detecting timezone...
  Timezone updated: America/New_York -> America/Denver (via GeoIP)

Syncing clock...
  Clock synchronized: Sun Mar 15 10:23:45 MDT 2026

=== Done ===
```

## Uninstall
```
sudo update-rc.d sync-clock remove
sudo rm /etc/init.d/sync-clock
sudo rm /usr/local/bin/sync-clock.sh /usr/local/bin/tz
```
