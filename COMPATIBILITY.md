# Compatibility

Initial deployment target: Batocera **43.1 x86_64 / Xorg**, Intel Core i5-12400F, NVIDIA RTX 3060 Ti, NVIDIA driver 590.48.01, Sunshine **2026.914.233613**.

The existing persistent 64-bit `libwayland-client.so.0` workaround is retained. This is a tested-machine configuration, not a blanket compatibility claim for every Batocera or GPU release.

## Validation status

- Ten updater integrity/failure and Linux service lifecycle tests passed on the target Batocera version; ShellCheck 0.11.0 passed locally and GitHub Actions passed on Ubuntu.
- Real Sunshine deployment: passed, using the existing persistent library workaround.
- X11 capture and H.264/HEVC NVENC initialization: passed.
- Web UI authentication endpoint reachable over LAN and Tailscale: passed before and after reboot (HTTP 401 without credentials).
- Real service stop/start cycle: passed with one Sunshine instance and the existing configuration retained.
- Automatic startup after an orderly Batocera reboot: passed, with one Sunshine instance and H.264/HEVC NVENC initialized.
- Client video/audio/controllers and existing pairing usability: pending hands-on verification.

These checks establish server startup and reachability. They do not establish client streaming quality or controller mapping correctness.
