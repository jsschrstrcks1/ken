# Clock Sync + Timezone Detection (Devuan/SysVinit)

Automatically syncs the system clock and detects timezone at boot and wake.
Includes a `tz` command with 1200+ cruise port lookup, fuzzy matching, and trip scheduling.

## What it does

### At boot and wake (`sync-clock.sh`)
1. Checks timezone schedule (trip itinerary) — no network needed
2. Falls back to IP geolocation (with caching and confidence check)
3. Falls back to alternate GeoIP provider
4. Force-syncs the clock using `ntpd -g -q` (with retry)

### The `tz` command

**Check status:**
```
tz
```
```
14:32  America/New_York  (UTC-05:00)

Trip:  tokyo -> los angeles
Source: schedule
Next:  May 28 -> America/Los_Angeles (los angeles)
```

**Set timezone by city name:**
```
tz tampa
tz cabo san lucas
tz barcelona
```

Fuzzy matching suggests corrections:
```
$ tz tamapa
'tamapa' not recognized.
Did you mean:
  tz tampa                     (America/New_York)
```

**Detect timezone from network:**
```
tz here
```

**Plan a trip:**
```
tz trip start 2027-05-12 tokyo
tz shimizu
tz nagoya
tz osaka
tz +kobe                       # same day as osaka
tz sea
tz sea
tz los angeles
```

When a trip is active, `tz <city>` adds to the itinerary instead of
changing the timezone immediately. The schedule auto-compiles on every
change. No `end` command needed (though `tz trip end` is available).

Auto-SEA inference inserts sea days when the timezone changes between ports.
Use `+port` for same-day ports (e.g. Osaka and Kobe on the same calendar day).
Use `tz sea` for explicit sea days.

**Load itinerary from a file:**
```
tz trip load ~/cruises/japan-2027.txt
```

File format (first line = start date, then one port per line):
```
2027-05-12
tokyo
shimizu
nagoya
osaka
+kobe
sea
sea
los angeles
```

**Search for cities:**
```
tz list caribbean
tz list mediterranean
```

**Remove a mistake:**
```
tz undo
```

**Other schedule commands:**
```
tz schedule                    # show schedule
tz schedule add <date> <city>  # add single entry
tz schedule clear              # remove all entries
```

Old schedule entries are automatically pruned.

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
