# Plan: Linux Clock Sync + Timezone Detection Startup Script

## Files to create

### 1. `sync-clock.sh` — The sync script
- Detect timezone via IP geolocation (ip-api.com) and set it with `timedatectl`
- Force-sync the clock using `ntpd -g -q` (one-time jump, then exit)
- Sync hardware clock with `hwclock --systohc`

### 2. `sync-clock.service` — systemd unit file
- `[Unit]` section: `Description`, `After=network-online.target`, `Wants=network-online.target`, `Before=ntpd.service`
- `[Service]` section: `Type=oneshot`, `ExecStart=/usr/local/bin/sync-clock.sh`
- `[Install]` section: `WantedBy=multi-user.target`

### 3. `README.md` — Installation instructions
- Copy script to `/usr/local/bin/`, make executable
- Copy service to `/etc/systemd/system/`
- `systemctl daemon-reload && systemctl enable sync-clock.service`
- Dependencies: curl, ntpd, timedatectl

## Implementation steps
1. Create `sync-clock.sh` with timezone detection and force time sync
2. Create `sync-clock.service` systemd unit
3. Create `README.md` with install steps and dependencies
4. Commit and push to branch
