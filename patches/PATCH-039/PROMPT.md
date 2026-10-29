# PATCH-039 integration prompt

Install the authored bridge as a persistent local file on the actual execution
host and custom SKILL.md in the existing Dewiar workspace skill directory.
Verify source hashes and current Manager CLI semantics before configuring it.
Do not overwrite upstream Dewiar or alter global model/Manager configuration.

Register a single MCP server `workbook` with `trust=false`, the exact native
Python, script path, host/source pins and current helper SHA256 arguments.
Keep credentials out of this public package. The separate approval directory
is local and root-owned under a protected root-owned path, without group/world
write permissions. Run the bridge as an unprivileged user; never grant it sudo.
Retain all unrelated settings and create a private rollback snapshot.

Read `core/mcp.py` and `core/skills.py` on the installed version. Verify
initialize, tools/list and actual read-only calls through that client, then
load the skill and check it is visible. For long catalogs/documents test
continuation pages and confirm no response is silently cut at 8000 chars.
Check that missing approvals, host mismatch, revision drift and native resume
blocks are refused without invoking a mutation. Use isolated Manager fixtures
for successful controls and idempotency. Preserve real paused tasks.

Report source integrity, live handshake, tool visibility, actual model tool
use and task execution separately. Do not call inference merely to validate
the protocol. If a model route lacks MCP support, record that limitation.
