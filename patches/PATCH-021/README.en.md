# PATCH-021 — Android control adapter

[RU](README.md) · [ENG](README.en.md) · [CH](README.zh.md)

Portable Windows control for an existing Android VM: authenticated HTTPS API, CLI, SSH wrappers and a configurable WireGuard routing guard. This is not an Android installer. Secrets, certificates, VM disks, guest keys and router configuration are not included.

[Integration contract](INTEGRATION.md) · [Prompt](PROMPT.md) · [Manifest](manifest.json). Use inspect before test. The control tests need src/android_control/control-requirements.txt; dependency installation is a separate step.

Offline contract tests PASS; installation, public network ingress and live VPN changes NOT_RUN in this delivery. [Current Android modules](../../android/ANDROID-005/README.md).
