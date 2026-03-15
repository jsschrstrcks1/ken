# Clock Sync + Timezone Detection (Devuan/SysVinit)

Automatically syncs the system clock and detects timezone at boot and wake.
Includes a `tz` command with 1200+ cruise port lookup and itinerary scheduling.

## What it does

### At boot and wake (`sync-clock.sh`)
1. Checks timezone schedule (cruise itinerary) — no network needed
2. Falls back to IP geolocation (before VPN connects)
3. Falls back to WiFi-based detection
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

**Search for timezones:**
```
tz list caribbean
tz list mediterranean
tz list alaska
```

**Build a cruise itinerary:**
```
tz cruise start 2026-02-24
tz cruise ensenada
tz cruise sea
tz cruise cabo san lucas
tz cruise sea
tz cruise los angeles
tz cruise end
```

This produces a schedule that auto-applies the correct timezone each morning:
```
DATE         TIMEZONE                     NOTE
----         --------                     ----
2026-02-24   America/Tijuana              ensenada
2026-02-25   America/Tijuana              SEA
2026-02-26   America/Mazatlan             cabo san lucas
2026-02-27   America/Mazatlan             SEA
2026-02-28   America/Los_Angeles          los angeles
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
- iw (for WiFi fallback)
- logger (bsdutils)
- acpid (for wake hook)

## Installation

1. Copy scripts and make them executable:
```
sudo cp sync-clock.sh /usr/local/bin/sync-clock.sh
sudo cp tz /usr/local/bin/tz
sudo chmod +x /usr/local/bin/sync-clock.sh /usr/local/bin/tz
```

2. Install the city mapping:
```
sudo cp tz-cities /usr/local/share/tz-cities
```

3. Install the init.d service:
```
sudo cp sync-clock /etc/init.d/sync-clock
sudo chmod +x /etc/init.d/sync-clock
sudo update-rc.d sync-clock defaults
```

4. Install the wake hook (requires acpid):
```
sudo apt install acpid
sudo cp tz-wakeup-event /etc/acpi/events/tz-wakeup
sudo cp tz-wakeup.sh /etc/acpi/tz-wakeup.sh
sudo chmod +x /etc/acpi/tz-wakeup.sh
sudo service acpid restart
```

5. (Optional) Test it now:
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
sudo rm /usr/local/bin/sync-clock.sh /usr/local/bin/tz
sudo rm /usr/local/share/tz-cities
sudo rm -f /etc/tz-schedule
sudo rm -f /etc/acpi/events/tz-wakeup /etc/acpi/tz-wakeup.sh
```
