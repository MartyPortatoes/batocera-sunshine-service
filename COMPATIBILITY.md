# Compatibility

Initial deployment target: Batocera **43.1 x86_64 / Xorg**, Intel Core i5-12400F, NVIDIA RTX 3060 Ti, NVIDIA driver 590.48.01, Sunshine **2026.914.233613**.

The existing persistent 64-bit `libwayland-client.so.0` workaround is retained. This is a tested-machine configuration, not a blanket compatibility claim for every Batocera or GPU release.

## Validation status

- Updater integrity/failure tests and Linux service lifecycle tests: passed on the target Batocera version.
- Real Sunshine deployment, encoder initialization, controller/streaming checks, and reboot persistence: pending.

Update this record with observed results before the first public release.
