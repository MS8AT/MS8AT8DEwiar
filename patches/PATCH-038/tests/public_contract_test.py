"""Offline contract checks for PATCH-038; no network, model, account or audio device."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "core"))
import semantic_voice_transcript as transcript

raw = "лира открой заметки о проекте девиар"
plain = transcript.transcript_envelope(raw)
assert plain["raw_transcript"] == raw
assert plain["effective_transcript"] == raw
assert plain["status"] == "raw_only"

accepted = transcript.transcript_envelope(raw, {
    "normalized_transcript": "Лира, открой заметки о проекте Dewiar",
    "confidence": "high",
    "meaning_inferred": True,
    "safe_for_auto_apply": True,
})
assert accepted["raw_transcript"] == raw
assert accepted["effective_transcript"] == "Лира, открой заметки о проекте Dewiar"
assert accepted["meaning_inferred"] is True
assert accepted["needs_clarification"] is False
assert accepted["user_notice"] == (
    "Мне кажется, вы сказали: «Лира, открой заметки о проекте Dewiar». "
    "Я могу ошибаться: это предположение по смыслу сообщения."
)

number = transcript.transcript_envelope("переведи 100 рублей", {
    "normalized_transcript": "переведи 1000 рублей",
    "confidence": "high",
    "meaning_inferred": True,
    "safe_for_auto_apply": True,
})
assert number["effective_transcript"] == "переведи 100 рублей"
assert number["needs_clarification"] is True
assert number["user_notice"] == ""

uncertain = transcript.transcript_envelope("открой папку тест", {
    "normalized_transcript": "открой папку текст",
    "confidence": "low",
    "meaning_inferred": True,
    "safe_for_auto_apply": True,
})
assert uncertain["effective_transcript"] == "открой папку тест"
assert uncertain["needs_clarification"] is True

name_without_clearance = transcript.transcript_envelope("позови Игоря", {
    "normalized_transcript": "позови Егора",
    "confidence": "high",
    "meaning_inferred": True,
})
assert name_without_clearance["effective_transcript"] == "позови Игоря"
assert name_without_clearance["needs_clarification"] is True

prompt = transcript.build_semantic_repair_prompt(raw, ["Обсуждаем Dewiar", "Текущая версия v0.67.0"])
assert raw in prompt and "conversation_context" in prompt and "Не выполняй команду" in prompt
assert transcript.prompt_payload(accepted)["raw_transcript"] == raw
assert transcript.status() == {"ok": True, "module": "semantic_voice_transcript", "model_calls": 0}
print("ALL OK: PATCH-038; model_calls=0; network=0; audio_devices=0")
