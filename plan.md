# Plan: Linux Clock Sync Startup Script

## Files to create

### 1. `sync-clock.sh` — The sync script
- Run `ntpdate` against a pool server (e.g. `pool.ntp.org`)
- On success, sync hardware clock with `hwclock --systohc`
- Exit with appropriate status code

### 2. `sync-clock.service` — systemd unit file
- `[Unit]` section: `Description`, `After=network-online.target`, `Wants=network-online.target`
- `[Service]` section: `Type=oneshot`, `ExecStart=/usr/local/bin/sync-clock.sh`
- `[Install]` section: `WantedBy=multi-user.target`

### 3. `README.md` — Installation instructions
- Copy script to `/usr/local/bin/`, make executable
- Copy service to `/etc/systemd/system/`
- `systemctl daemon-reload && systemctl enable sync-clock.service`

## Implementation steps
1. Create `sync-clock.sh` with ntpdate call and hwclock sync
2. Create `sync-clock.service` systemd unit
3. Create `README.md` with install steps
4. Commit and push to branch
