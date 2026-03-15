# Clock Sync + Timezone Detection (Devuan/SysVinit)

Automatically syncs the system clock and detects timezone at boot.
Includes a `tz` command with city lookup, timezone search, and cruise itinerary scheduling.

## What it does

### At boot (`sync-clock.sh`)
1. Checks timezone schedule (cruise itinerary) — no network needed
2. Falls back to IP geolocation (before VPN connects)
3. Falls back to WiFi-based detection
4. Force-syncs the clock using `ntpd -g -q`
5. Displays results on screen for 3 seconds

### The `tz` command

**Set timezone by city name:**
```
tz tampa
tz cabo san lucas
tz barcelona
```

**Search for timezones:**
```
tz list caribbean
tz list mediterranean
tz list pacific
```

**Schedule a cruise itinerary:**
```
tz schedule add 2026-02-24 ensenada Port day
tz schedule add 2026-02-25 cabo Day trip
tz schedule add 2026-02-26 los angeles Disembark
tz schedule add 2026-02-27 tampa Fly home
```

**View and manage schedule:**
```
tz schedule              # show itinerary
tz schedule clear        # remove all entries
tz                       # show current timezone + next scheduled change
```

## Boot output example
```
=== Clock Sync ===

Detecting timezone...
  Timezone updated: America/New_York -> America/Tijuana (via schedule)

Syncing clock...
  Clock synchronized: Tue Feb 24 08:15:23 PST 2026

=== Done ===
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

4. (Optional) Test it now:
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
```
