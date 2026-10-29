# PATCH-038 integration prompt — Dewiar 0.67.0

Target the clean commit `80f1870074dbde643855b2b0ff1c40d7496dcb4c`.
Verify and test the block before adding the authored module; do not replace
existing upstream files. Decision contract revision 2 is a breaking change
for callers that previously assumed effective_transcript was always a string.

After STT language selection, preserve the exact string in raw_transcript.
Emit it as a labelled original in the hearing event. An explicitly configured
adapter may receive build_semantic_repair_prompt(raw, conversation_context)
and return only the documented JSON. A model safety flag is untrusted input,
not permission to alter names, exact identifiers or execute actions.

Pass the result through transcript_envelope. Always render raw and proposed
normalized variants separately and display user_notice for every change.
Only dispatch when can_dispatch is true AND needs_clarification is false AND
effective_transcript is a nonempty string. On clarification or malformed
candidate, effective_transcript is null: ask clarification_prompt and stop the
action path. Never substitute raw_transcript as a fallback command. The new
explicit answer from the person goes through the ordinary permission gates.

Any lexical change requires clarification, including apparent typos or an
unknown name. Automatic changes are limited to case/whitespace, high
confidence, explicit safety flag, no protected token. This deterministic
policy cannot certify arbitrary names; do not claim it can.

Wire the core path in engine_audio.py and the labelled hearing consumer in
ui/studio/connect.js only in an isolated candidate. Add regression cases for
blocked dispatch, changed names, empty/malformed model output and exact raw
preservation. Run core/UI checks with temporary state. Network/model/device
installation and live acceptance are separate operations.
