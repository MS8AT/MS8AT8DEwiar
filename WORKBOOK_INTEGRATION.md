# Dewiar and WorkBook integration

PATCH-038 revision 2 and PATCH-039 are authored standalone modules. The public
kit does not redistribute the Dewiar source tree or private runtime settings.

PATCH-038 preserves raw transcript whitespace exactly. Every changed proposal
has an uncertainty notice. Lexical changes require clarification, including
unknown names that a regular expression cannot identify reliably. A blocked
or malformed proposal returns `can_dispatch=false` and no effective command.
Model self-assessment is not execution authority. The envelope still requires
Engine/UI integration; publishing it does not enable speech correction.

PATCH-039 runs next to Dewiar using its supported stdio MCP configuration and
custom skills. It reads the existing WorkBook registry and native Manager;
it exposes no generic terminal, model endpoint, task admission or dispatch.
Control is limited to exact task pause/stop/resume with externally created,
protected operator grants. The approval and task revision are checked again
inside the existing Manager transaction. No additional task database is made.

The MCP and skills clients of installed Dewiar 0.45.3 and upstream 0.67.0 are
byte-identical in the tested copies. This establishes the bridge protocol
compatibility, not a full application overlay upgrade. SHA-256:

- MCP client: `3971849809e9723852301e315af426ac60427ff240ef5b5815f906950e980f83`.
- Skills: `0a895106830ecf26a4bec7976efe64261d62fab81da94ea7a1984a3873de48d5`.

Verification on 2026-10-29:

- PATCH-038: 17 offline tests; exact additive apply/hash/reverse on clean 0.67.0.
- PATCH-039: 21 offline tests on Windows and Linux, including schema/host checks,
  protected approvals, stale revisions under lock, idempotency and lost receipts.
- Existing Manager: 12 native tests on disposable real Manager/Registry stores;
  operational database hashes unchanged before/after.
- Installed Dewiar client: handshake, seven tools, six actual read/preview
  calls, catalog/document pagination, and refusal of an unapproved write.
- Live Dewiar: MCP status `ok`, enabled custom skill visible to model prompt,
  explicit write-tool confirmation enabled. LLM/audio settings preserved.

Real model inference, physical audio and successful control of a real task
were not run. A task requiring native saved-project binding remains blocked.
The global project-index checker also reported existing search/index problems;
the bridge uses the existing valid module registry and does not repair ACLs or
rebuild unrelated indexes automatically.

If receipt delivery fails after a control begins, keep its task/request ID and
reconcile the native Manager before retrying. `stopping` means a stop is pending;
`resume` only changes task control and never proves work was dispatched.
