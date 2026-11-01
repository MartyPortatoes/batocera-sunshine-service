# Batocera Sunshine Service

A Batocera user service for the official [Sunshine](https://github.com/LizardByte/Sunshine) AppImage. Based on [n2qz/batocera-service-sunshine](https://github.com/n2qz/batocera-service-sunshine), with credit to maximumentropy/n2qz. Distributed under the same CC0-1.0 license.

This project maintains the Batocera integration; Sunshine itself remains an upstream LizardByte project.

## Features

- Offline boot: the service starts a locally installed, version-pinned AppImage.
- Explicit updates from official GitHub releases, with architecture selection, published SHA-256 verification, and atomic activation.
- Current versioned and older `sunshine.AppImage` asset names are recognized. Releases without a published digest are refused.
- Persistent configuration, applications, credentials, and Moonlight pairings.
- An optional compatibility-library directory, without replacing system libraries.
- Idempotent startup, process-group shutdown, PID reuse protection, and append-only service logging.

## Requirements

Batocera x86_64 using Xorg, Bash, Python 3.9+, `setsid`, `flock`, and the standard Linux process tools. ARM and Wayland hosting are outside the initial support scope.

The service runs as root, as Batocera user services normally do. The configuration file is trusted Bash code; keep it root-owned and private.

## Install or migrate

Download a tagged project release or clone this repository, inspect the scripts, and run them on Batocera. For an existing n2qz installation, stop the old service first:

```bash
batocera-services stop sunshine
bash install.sh 2026.914.233613
batocera-services enable sunshine
batocera-services start sunshine
```

The installer verifies the AppImage before replacing the service. It keeps existing Sunshine data under `/userdata/system/.config/sunshine` and installs the updater under `/userdata/system/bin`. The original AppImage is not removed.

For a new installation, enable **Sunshine** under **System Settings → Services**, then open `https://<batocera-address>:47990` and follow the upstream pairing instructions.

## Manual updates

```bash
# Inspect the latest stable release without installing:
/userdata/system/bin/sunshine-update --check

# Download a pinned release without changing the active version:
/userdata/system/bin/sunshine-update 2026.914.233613

# Select a verified release and restart the service explicitly:
/userdata/system/bin/sunshine-update 2026.914.233613 --activate --restart

# Or explicitly select the latest stable release:
/userdata/system/bin/sunshine-update stable --activate --restart
```

Boot and status checks never contact GitHub. Updates do not select prereleases automatically. A failed download or checksum leaves the selected AppImage unchanged. Existing verified downloads can be reused, although resolving release metadata still requires GitHub access.

## Configuration and compatibility libraries

Copy `sunshine-service.conf.example` to `/userdata/system/configs/sunshine-service.conf` if needed. Defaults use display `:0.0`, disable the system tray, and prepend `/userdata/system/extra-libs` to the process's library search path.

Some Batocera 43.1 installations need a compatible **64-bit** `libwayland-client.so.0` even when capturing Xorg. Supply it from a trusted, license-compliant distribution in a persistent directory and configure `SUNSHINE_LIBRARY_PATH`. This repository does not bundle that library or install arbitrary system packages. Recheck ABI compatibility after OS or Sunshine updates.

## Troubleshooting

```bash
batocera-services status sunshine
tail -100 /userdata/system/logs/sunshine.log
```

- A running process or reachable web UI does not prove streaming works. Check hardware encoder detection, video, audio, controllers, and game launch/exit with Moonlight.
- Recent Sunshine releases changed virtual input. Check `/dev/uhid`, `/dev/uinput`, and controller mappings if input changes after an update.
- On supported NVIDIA hardware, expect H.264 and/or HEVC NVENC. Unsupported AV1 probing is not by itself a failure.
- Keep Sunshine's Web UI authentication enabled. Do not post credentials, pairing state, or unredacted configuration/logs in issues.
- Configuration and pairing state stay in userdata, but OS updates can still change libraries, drivers, and input support. Test again after reboot.

## Remove the integration

Stop and disable the service, then remove only its service script and updater:

```bash
batocera-services stop sunshine
batocera-services disable sunshine
rm /userdata/system/services/sunshine /userdata/system/bin/sunshine-update
```

Sunshine configuration, pairings, downloaded AppImages, logs, and optional compatibility libraries remain available for deliberate manual cleanup.

## Development

```bash
bash -n sunshine install.sh
shellcheck sunshine install.sh
python3 -m unittest discover -s tests -v
```

The service lifecycle tests run on Linux; updater tests also run on macOS. GitHub Actions runs both on Ubuntu. Test fixtures use temporary directories and mock downloads; they do not operate the installed Sunshine service.

Live compatibility results are recorded in [COMPATIBILITY.md](COMPATIBILITY.md). Further Batocera versions and GPU combinations require their own validation.
