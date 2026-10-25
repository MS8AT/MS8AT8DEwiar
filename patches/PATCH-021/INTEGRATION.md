# Integration contract / Контракт / 集成契约

Responsibility: control a provisioned Windows-hosted Android VM. Inputs are explicit authenticated actions, local deployment metadata and runner state. Outputs are bounded JSON, audit events and queued VPN results. Side effects are explicit VM lifecycle, Android window/lock settings, Startup shortcuts and the guest VPN guard. No model inference or account login is included.

## Prerequisites

- A Windows runtime directory owned by the current user; an existing verified `runtime.py`, QEMU under `qemu/`, ADB under `platform-tools/`, persistent disk and Android payload. The runner must consume the queue contract below. This patch deliberately does not ship or import that runner.
- Python 3.10+, the packages in `control-requirements.txt`, and a local `python-path.txt`. Dependencies can be installed in an isolated environment or `vendor/`; do not modify Dewiar's bundled packages.
- `credentials/` restricted to the current user and SYSTEM. Provision this ACL **before** starting the controller. The controller assumes the ACL; it does not install or audit ACLs.
- `android_ed25519.pub` contains the approved client public key. The client keeps `android_ed25519` protected and pins the server key in `known_hosts`. No password auth, forwarding or host shell is enabled.
- On first explicit controller start, missing `api-token.txt`, TLS key/certificate and SSH host key are generated only in that protected directory. Existing material is preserved. Distribute the API certificate and SSH public host key through a trusted path; never disable host verification. The TLS certificate lifetime is one year; renewal is an operator action.
- `control-deployment.json` is local endpoint metadata, not a secret. A missing file uses loopback only. Invalid configuration prevents controller startup. Allowed fields: `bind_host` (127.0.0.1 or 0.0.0.0), `certificate_hosts` (1–16 exact IPv4/DNS names, always including 127.0.0.1 for the local CLI/menu). No wildcards/URLs/shell strings. `SSH.ps1` independently checks its target against the host list and a hostname pattern; it does not validate the controller's bind setting.

Copy the controller source to a **stopped, backed-up candidate runtime**, not over a live runner. Render `guest-wg.sh.in` through `configure.py`; inspect the candidate before placement. Keep the existing `runtime.py` and payload manifests. The currently verified runner computes the guest helper's SHA before serving it. If another runner uses separate helper pins, update only its declared pin after review. Do not overwrite the full helper-hash manifest or APK pins.

## Runner state and lifecycle

`state.json` is atomically replaced by the existing runner. Control reads: `status`, `phase`, `health`, `vm_running`, `android_boot_completed`, `app_process_alive`, `ram_mib`, `updated_at`, `vpn_boot_setup`, `vpn_interface_up`. SSH and Android shell actions require `phase=ready`, `vm_running=true`, and `adb_serial=127.0.0.1:<port>`. Lifecycle/Startup actions and VPN queue submission do not require ready state; queued work can remain pending without a runner. Status older than 90 seconds is marked stale; it is not proof of current health.

PowerShell lifecycle helpers also consume `pid` and `runner_pid` and check paths/runner command identity. `Stop.ps1` requests graceful stop; an orphan VM is reported, not force-killed. `Start.ps1` rejects a known orphan to avoid two writers to one disk. This does not guarantee crash recovery when state is missing; reconcile process and disk ownership first.

## API and CLI

Every route requires `Authorization: Bearer <protected local token>` over HTTPS. Unauthenticated calls return 401. No tokens or command bodies enter the audit log.

| Method | Route | Result |
|---|---|---|
| GET | `/v1/status` | runner status and settings; unavailable → 503 |
| GET | `/v1/capabilities` | fixed actions and sizes |
| GET | `/v1/logs` | last 100 allowlisted audit events, bounded read |
| GET | `/v1/requests/<32 hex ID>` | result, or pending 202 |
| POST | `/v1/action` | one fixed action; malformed parameters → 400 |

POST body is at most 4096 bytes. Actions: `start`, `stop`, `open`, `screen` with size `800x500/960x600/1280x800`, `lock/autostart/vpn` with boolean `enabled`, `vpn-status`. The queue can acknowledge acceptance before completion. Unknown result IDs remain pending; clients must keep the ID from the accepted action. There is no automatic retry after ambiguity.

CLI exit 0 means a successful response, not necessarily a healthy VM; inspect `android.health`, `stale` and `vm_running`. Exit 1 means failure; exit 3 means an accepted request is still pending after the bounded poll. Reconcile `/v1/requests/<ID>` before sending the action again.

## VPN queue and guest contract

Controller atomically writes `requests/<ID>.json`: `{action: vpn_up|vpn_down|vpn_status, created_ns: integer}`. The runner calls `pending_requests`, executes only `up/down/status`, and uses `write_result` with `{ok: boolean, output: string}`. Queue order follows timestamp, not random UUID. Corrupt entries get individual failures. Queue cleanup/retention is not included; archive finished entries only after reconciliation.

The guard targets the verified QEMU user-network topology: `eth0`, guest subnet 10.0.2.0/24, host alias 10.0.2.2, bootstrap HTTP 10.0.2.100, local ADB replies. The endpoint is rendered as an exact IPv4/UDP port. It changes only `MS8AT_WG_OUT`, its OUTPUT hook, an IPv6 eth0 reject, and management route table 59999/preference 9000. Do not reuse reserved identifiers in a conflicting guest network.

The guest already needs root-owned `/data/misc/ms8at`, verified WireGuard tools under `bin/`, protected `dewiarwg.conf` and interface name `dewiarwg`. The guard does not provision these. It preserves management connectivity and blocks direct guest Internet when VPN is down. It is a routing guard for this lab, not a hardened boundary against a privileged guest.

Router-side peer/NAT/routing and WAN SSH/API forwarding are separate deployment steps. Their private addresses/keys are not part of this patch. Existing phone profiles must be preserved.

## Separate language integration

Apply ANDROID-001 only to its recorded source base in a separate checkout, run its tests, then build and verify an APK. Keep signing identity stable. If a signature must change, use a separately reviewed data migration and a verified cold disk backup; this control patch does not uninstall an app or migrate signatures.
