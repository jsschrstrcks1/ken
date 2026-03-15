#!/bin/bash
set -euo pipefail

# Install script for tz + sync-clock
# Usage: sudo ./install.sh

if [ "$(id -u)" -ne 0 ]; then
    echo "Run with sudo: sudo ./install.sh"
    exit 1
fi

DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing tz..."

# Scripts (install with explicit ownership and permissions)
install -o root -g root -m 755 "$DIR/sync-clock.sh" /usr/local/bin/sync-clock.sh
install -o root -g root -m 755 "$DIR/tz" /usr/local/bin/tz
install -o root -g root -m 755 "$DIR/tz-network-check" /usr/local/bin/tz-network-check

# City mapping
install -o root -g root -m 644 "$DIR/tz-cities" /usr/local/share/tz-cities

# State and cache directories (root-only access)
mkdir -p /var/lib/tz /var/cache/tz
chmod 700 /var/lib/tz /var/cache/tz
chown root:root /var/lib/tz /var/cache/tz

# init.d service
install -o root -g root -m 755 "$DIR/sync-clock" /etc/init.d/sync-clock
update-rc.d sync-clock defaults 2>/dev/null || true

# Wake hook (acpid)
if command -v acpid >/dev/null 2>&1 || dpkg -l acpid >/dev/null 2>&1; then
    install -o root -g root -m 644 "$DIR/tz-wakeup-event" /etc/acpi/events/tz-wakeup
    install -o root -g root -m 755 "$DIR/tz-wakeup.sh" /etc/acpi/tz-wakeup.sh
    service acpid restart 2>/dev/null || true
    echo "  Wake hook installed (acpid)"
else
    echo "  Skipping wake hook (install acpid for resume detection)"
fi

# Network change hook
if [ -d /etc/network/if-up.d ]; then
    install -o root -g root -m 755 "$DIR/tz-network-check" /etc/network/if-up.d/tz-network-check
    echo "  Network hook installed"
fi

echo "Done. Try: tz"
