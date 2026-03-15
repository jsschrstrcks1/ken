# Clock Sync + Timezone Detection (Devuan/SysVinit)

Automatically syncs the system clock and detects timezone at boot.
Includes a manual `tz` command for reliable timezone changes when traveling.

## What it does

### At boot (`sync-clock.sh`)
1. Detects your timezone via IP geolocation (before VPN connects)
2. Updates `/etc/timezone` and `/etc/localtime` if timezone changed
3. Force-syncs the clock using `ntpd -g -q` (allows large time jumps)
4. Writes corrected time to the hardware clock

If GeoIP detection fails (VPN, captive portal, etc.), it logs the failure
and continues with the existing timezone. Use the `tz` command to fix it manually.

### Manual timezone change (`tz`)
```
tz America/Denver
tz Europe/London
tz                    # show current timezone
```

## Dependencies
- curl
- ntpd
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

## Uninstall
```
sudo update-rc.d sync-clock remove
sudo rm /etc/init.d/sync-clock
sudo rm /usr/local/bin/sync-clock.sh /usr/local/bin/tz
```
