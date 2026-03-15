# Clock Sync + Timezone Detection (Devuan/SysVinit)

Automatically syncs the system clock and detects timezone at boot and wake.
Includes a `tz` command with 1200+ cruise port lookup and itinerary scheduling.

## What it does

### At boot and wake (`sync-clock.sh`)
1. Checks timezone schedule (cruise itinerary) — no network needed
2. Falls back to IP geolocation (before VPN connects)
3. Falls back to alternate GeoIP provider
4. Force-syncs the clock using `ntpd -g -q` (with retry)
5. Displays results on screen for 3 seconds

### The `tz` command

**Set timezone by city name (1200+ ports):**
```
tz tampa
tz cabo san lucas
tz barcelona
tz santorini
```

**Detect timezone from network (no reboot needed):**
```
tz here
```

**Show current timezone state and diagnostics:**
```
tz explain
```

**Search for timezones:**
```
tz list caribbean
tz list mediterranean
tz list alaska
```

**Build a cruise itinerary:**
```
tz cruise start 2027-05-12
tz cruise tokyo
tz cruise shimizu
tz cruise nagoya
tz cruise osaka
tz cruise osaka
tz cruise +kobe              # same day as osaka
tz cruise sea
tz cruise sea
tz cruise sea
tz cruise los angeles
tz cruise end
```

Auto-SEA inference inserts sea days when the timezone changes between ports.
Use `+port` for same-day ports (e.g. Osaka and Kobe on the same calendar day).
Use explicit `tz cruise sea` for multi-day ocean crossings.

**Load itinerary from a file:**
```
tz cruise load ~/cruises/japan-2027.txt
```

File format (first line = start date, then one port per line):
```
2027-05-12
tokyo
shimizu
nagoya
osaka
osaka
+kobe
sea
sea
sea
los angeles
```

This produces a schedule that auto-applies the correct timezone each morning:
```
DATE         TIMEZONE                     NOTE
----         --------                     ----
2027-05-12   Asia/Tokyo                   tokyo
2027-05-13   Asia/Tokyo                   shimizu
2027-05-14   Asia/Tokyo                   nagoya
2027-05-15   Asia/Tokyo                   osaka
2027-05-16   Asia/Tokyo                   osaka
2027-05-16   Asia/Tokyo                   kobe (same day)
2027-05-17   Asia/Tokyo                   SEA
2027-05-18   Asia/Tokyo                   SEA
2027-05-19   Asia/Tokyo                   SEA
...
2027-05-28   America/Los_Angeles          los angeles
```

**Other schedule commands:**
```
tz schedule                  # show schedule
tz schedule add <date> <city>  # add single entry
tz schedule clear            # remove all entries
tz undo                      # remove last entry
```

**Manual timezone change:**
```
tz America/Denver
tz                           # show current timezone
```

## Dependencies
- curl
- ntpd
- logger (bsdutils)
- acpid (for wake hook)
- wireless-tools (optional, for `iwgetid` in network change detection)

## Installation

1. Copy scripts and make them executable:
```
sudo cp sync-clock.sh /usr/local/bin/sync-clock.sh
sudo cp tz /usr/local/bin/tz
sudo cp tz-network-check /usr/local/bin/tz-network-check
sudo chmod +x /usr/local/bin/sync-clock.sh /usr/local/bin/tz /usr/local/bin/tz-network-check
```

2. Install the city mapping:
```
sudo cp tz-cities /usr/local/share/tz-cities
```

3. Create state and cache directories:
```
sudo mkdir -p /var/lib/tz /var/cache/tz
```

4. Install the init.d service:
```
sudo cp sync-clock /etc/init.d/sync-clock
sudo chmod +x /etc/init.d/sync-clock
sudo update-rc.d sync-clock defaults
```

5. Install the wake hook (requires acpid):
```
sudo apt install acpid
sudo cp tz-wakeup-event /etc/acpi/events/tz-wakeup
sudo cp tz-wakeup.sh /etc/acpi/tz-wakeup.sh
sudo chmod +x /etc/acpi/tz-wakeup.sh
sudo service acpid restart
```

6. (Optional) Install network change hook:
```
sudo cp tz-network-check /etc/network/if-up.d/tz-network-check
sudo chmod +x /etc/network/if-up.d/tz-network-check
```

7. (Optional) Test it now:
```
sudo /etc/init.d/sync-clock start
```

## Adding custom cities

Edit `/usr/local/share/tz-cities` and add entries at the bottom:
```
my hometown|America/Chicago
the office|America/New_York
```

## Uninstall
```
sudo update-rc.d sync-clock remove
sudo rm /etc/init.d/sync-clock
sudo rm /usr/local/bin/sync-clock.sh /usr/local/bin/tz /usr/local/bin/tz-network-check
sudo rm /usr/local/share/tz-cities
sudo rm -f /etc/tz-schedule
sudo rm -rf /var/lib/tz /var/cache/tz
sudo rm -f /etc/acpi/events/tz-wakeup /etc/acpi/tz-wakeup.sh
sudo rm -f /etc/network/if-up.d/tz-network-check
```
