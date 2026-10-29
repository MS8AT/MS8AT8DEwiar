# PATCH-038 integration prompt — Dewiar 0.67.0

Target only a clean checkout at commit
`80f1870074dbde643855b2b0ff1c40d7496dcb4c`. First verify and test this
block, then add `src/core/semantic_voice_transcript.py` as a new file. Do not
replace any existing upstream file.

In `core/engine_audio.py`, keep the STT output as `raw_transcript` after
language selection and before `handle_text` / `handle_held`. Always emit the
raw text in the existing `hearing` event. Semantic repair is opt-in: only an
explicitly configured adapter may receive `build_semantic_repair_prompt(raw,
conversation_context)` and return the documented JSON candidate. It must set
`safe_for_auto_apply` only if it found no changed name or other protected
entity; a missing flag fails closed. Do not call a cloud model by default and
do not retain audio.

Pass every candidate through `transcript_envelope`. When it returns
`accepted_with_notice`, display raw and normalized variants separately and
announce `user_notice` before dispatching `effective_transcript`. When it
returns `clarification_required`, show the raw text and ask
`clarification_prompt`; do not dispatch a task, action, payment, deletion,
tool call, or model request from that candidate. Preserve the normal path when
no adapter is configured.

Update the `hearing` event consumer in `ui/studio/connect.js` only to render
the two labelled variants and notice; it must not overwrite the raw line.
Add focused core and UI regression tests plus the relevant quick-test entry.
Run them in isolated state. Do not install Dewiar, start microphone capture,
send data to an account, or use real model inference as part of this change.
