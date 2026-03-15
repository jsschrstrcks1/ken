# Clock Sync + Timezone Detection (Devuan/SysVinit)

Automatically syncs the system clock and detects timezone at boot, wake, and
network change. Includes a `tz` command with 1200+ cruise port lookup, fuzzy
matching, and trip scheduling.

## What it does

### At boot and wake (`sync-clock.sh`)
1. Checks timezone schedule (trip itinerary) — no network needed
2. Falls back to IP geolocation (with caching and confidence check)
3. Falls back to alternate GeoIP provider
4. Force-syncs the clock using `ntpd -g -q` (with retry)

### On network change (`tz-network-check`)
Runs automatically when a network interface comes up. Detects SSID and
gateway changes and triggers timezone detection when the network fingerprint
changes. Throttled to once per 5 minutes.

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

### Prerequisites

```
sudo apt install curl ntp acpid wireless-tools
```

`acpid` enables wake-from-sleep detection. `wireless-tools` provides
`iwgetid` for WiFi SSID detection on network changes. Both are optional
but recommended.

### Install

```
git clone <repo-url> && cd ken
sudo ./install.sh
```

This installs:
- `/usr/local/bin/sync-clock.sh` — boot/wake timezone detection and NTP sync
- `/usr/local/bin/tz` — timezone helper command
- `/usr/local/bin/tz-network-check` — network change trigger
- `/usr/local/share/tz-cities` — city-to-timezone mapping (1200+ ports)
- `/etc/init.d/sync-clock` — SysVinit service (runs at boot)
- `/etc/acpi/tz-wakeup.sh` — ACPI wake hook (if acpid is installed)
- `/etc/network/if-up.d/tz-network-check` — network interface hook

State directories (`/var/lib/tz/`, `/var/cache/tz/`) are created with
mode `0700` and owned by root.

### Verify

```
tz                   # show current timezone status
tz here              # detect timezone from network
tz list caribbean    # search city database
```

## Security

All scripts run as root (boot, wake, and network hooks). The following
hardening measures are in place:

- **Timezone validation**: all timezone strings are validated against
  `^[A-Za-z0-9_/+-]+$` and rejected if they contain `..` (path traversal).
  This applies to GeoIP API responses, cache reads, and user input.
- **Atomic file writes**: state files (`/var/cache/tz/`, `/var/run/`) are
  written via temp file + `mv` to prevent symlink attacks.
- **Restrictive permissions**: state directories are `0700 root:root`.
  Installed scripts use `install(1)` with explicit ownership.
- **Concurrency control**: `sync-clock.sh`, `tz-network-check`, and
  `tz-wakeup.sh` all use `flock` to prevent race conditions from
  concurrent triggers.
- **Input sanitization**: WiFi SSIDs are stripped of non-printable
  characters and truncated to 32 bytes. Cooldown/timestamp files are
  validated as numeric before use in arithmetic.
- **No shell injection**: AWK variables are passed via `-v` (not string
  interpolation). `grep -F` is used for user-supplied search terms.
  `sed` with user-controlled delimiters has been replaced with
  `grep -Fxv`.
- **curl `--fail`**: HTTP error pages (4xx/5xx) are rejected rather than
  accepted as timezone data.

## Files

| File | Location | Purpose |
|------|----------|---------|
| `sync-clock.sh` | `/usr/local/bin/` | Boot/wake timezone detection + NTP sync |
| `tz` | `/usr/local/bin/` | Timezone helper command |
| `tz-network-check` | `/usr/local/bin/` + `/etc/network/if-up.d/` | Network change trigger |
| `tz-cities` | `/usr/local/share/` | City-to-timezone mapping |
| `sync-clock` | `/etc/init.d/` | SysVinit boot service |
| `tz-wakeup-event` | `/etc/acpi/events/` | ACPI event definition |
| `tz-wakeup.sh` | `/etc/acpi/` | Wake hook script |

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
sudo rm -f /var/run/tz.lock /var/run/tz-network-check.lock /var/run/tz-wakeup.lock
sudo rm -f /var/run/last-clock-sync
```
