#!/bin/bash
set -euo pipefail
SOURCE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT=${SUNSHINE_SERVICE_ROOT:-/userdata/system}
if [[ "$ROOT" == /userdata/system && "$EUID" -ne 0 ]]; then
    echo 'Run as root on Batocera.' >&2
    exit 1
fi
command -v python3 >/dev/null
command -v setsid >/dev/null
command -v flock >/dev/null
mkdir -p "$ROOT/services" "$ROOT/bin" "$ROOT/configs" "$ROOT/logs"
# Verify and select the artifact before replacing an existing service.
"$SOURCE/sunshine-update" "${1:-stable}" --activate
install -m 755 "$SOURCE/sunshine" "$ROOT/services/sunshine.staged"
install -m 755 "$SOURCE/sunshine-update" "$ROOT/bin/sunshine-update.staged"
mv -f "$ROOT/services/sunshine.staged" "$ROOT/services/sunshine"
mv -f "$ROOT/bin/sunshine-update.staged" "$ROOT/bin/sunshine-update"
if [[ ! -f "$ROOT/configs/sunshine-service.conf" ]]; then
    install -m 600 "$SOURCE/sunshine-service.conf.example" "$ROOT/configs/sunshine-service.conf"
fi
echo 'Enable SUNSHINE in Batocera System Settings > Services, or restart the existing service.'
