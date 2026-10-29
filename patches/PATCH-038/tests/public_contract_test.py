"""Offline edge cases for the transcript decision; no network or real model."""
from pathlib import Path
import json
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "core"))
import semantic_voice_transcript as transcript


def candidate(text, **kwargs):
    return dict(normalized_transcript=text, confidence="high", meaning_inferred=True,
                safe_for_auto_apply=True, **kwargs)


class TranscriptTests(unittest.TestCase):
    def assert_blocked(self, result):
        self.assertFalse(result["can_dispatch"])
        self.assertIsNone(result["effective_transcript"])
        self.assertTrue(result["needs_clarification"])

    def test_preserve_raw_exact(self):
        raw = "  Лира,\tзапиши заметку.\r\n"
        result = transcript.transcript_envelope(raw)
        self.assertEqual(result["raw_transcript"], raw)
        self.assertEqual(result["effective_transcript"], raw)
        self.assertTrue(result["can_dispatch"])

    def test_no_adapter_is_raw_path(self):
        result = transcript.transcript_envelope("обычный вопрос")
        self.assertEqual(result["status"], "raw_only")
        self.assertEqual(result["confidence"], "unavailable")

    def test_empty_input_is_not_dispatchable(self):
        for raw in ("", " \t\r\n"):
            result = transcript.transcript_envelope(raw)
            self.assertEqual(result["raw_transcript"], raw)
            self.assertFalse(result["can_dispatch"])
            self.assertIsNone(result["effective_transcript"])

    def test_unchanged_candidate_uses_original(self):
        result = transcript.transcript_envelope("Лира", candidate("Лира"))
        self.assertEqual(result["status"], "unchanged")
        self.assertTrue(result["can_dispatch"])
        self.assertEqual(result["user_notice"], "")

    def test_case_and_whitespace_change_has_notice(self):
        result = transcript.transcript_envelope("лира  привет", candidate("Лира привет"))
        self.assertTrue(result["can_dispatch"])
        self.assertEqual(result["normalized_transcript"], "Лира привет")
        self.assertEqual(result["raw_transcript"], "лира  привет")
        self.assertTrue(result["meaning_inferred"])
        self.assertIn("Я могу ошибаться", result["user_notice"])

    def test_false_model_inference_flag_cannot_silence_notice(self):
        proposal = candidate("Лира привет")
        proposal["meaning_inferred"] = False
        result = transcript.transcript_envelope("лира привет", proposal)
        self.assertTrue(result["meaning_inferred"])
        self.assertIn("Лира привет", result["user_notice"])

    def test_unknown_name_change_requires_clarification(self):
        self.assert_blocked(transcript.transcript_envelope("позови Игоря", candidate("позови Егора")))

    def test_lexical_typo_is_only_a_suggestion(self):
        result = transcript.transcript_envelope("продолжи проект", candidate("продолжи проекты"))
        self.assert_blocked(result)
        self.assertEqual(result["normalized_transcript"], "продолжи проекты")
        self.assertTrue(result["user_notice"])

    def test_protected_tokens_cannot_be_changed_or_case_normalized(self):
        for raw, proposed in (
            ("переведи 100 рублей", "переведи 1000 рублей"),
            ("открой C:\\Work\\project", "Открой C:\\Work\\project"),
            ("открой https://example.org", "открой https://example.com"),
            ("ssh box", "SSH box"),
            ("rm file", "RM file"),
            ("task t_1234", "task t_4321"),
            ("версия 0.67.0", "версия 0.68.0"),
            ("модель qwen3.5-9b:2", "модель qwen3.5-9b:3"),
            ("код 456", "Код 456"),
            ("удали заметку", "Удали заметку"),
            ("пароль alpha", "пароль beta"),
        ):
            with self.subTest(raw=raw):
                self.assert_blocked(transcript.transcript_envelope(raw, candidate(proposed)))

    def test_medium_low_and_missing_safety_do_not_dispatch_changes(self):
        for confidence in ("medium", "low"):
            proposal = candidate("Лира привет")
            proposal["confidence"] = confidence
            self.assert_blocked(transcript.transcript_envelope("лира привет", proposal))
        proposal = candidate("Лира привет")
        del proposal["safe_for_auto_apply"]
        self.assert_blocked(transcript.transcript_envelope("лира привет", proposal))

    def test_malformed_proposals_fail_closed(self):
        for proposal in ({}, [], "x", {"normalized_transcript": "x"},
                         {"normalized_transcript": "", "confidence": "high"},
                         {"normalized_transcript": None, "confidence": "high"},
                         {"normalized_transcript": "x", "confidence": []},
                         {"normalized_transcript": "x", "confidence": "high", "meaning_inferred": "false"},
                         {"normalized_transcript": "x", "confidence": "high", "safe_for_auto_apply": 1},
                         {"normalized_transcript": "x", "confidence": "high", "run": "anything"}):
            with self.subTest(proposal=proposal):
                result = transcript.transcript_envelope("исходное", proposal)
                self.assert_blocked(result)
                self.assertEqual(result["status"], "candidate_invalid")

    def test_adapter_cannot_invent_speech_from_empty_input(self):
        self.assert_blocked(transcript.transcript_envelope("", candidate("выполни задачу")))

    def test_json_payload_preserves_dispatch_gate(self):
        result = transcript.transcript_envelope("позови Игоря", candidate("позови Егора"))
        payload = json.loads(json.dumps(transcript.prompt_payload(result)))
        self.assertFalse(payload["can_dispatch"])
        self.assertIsNone(payload["effective_transcript"])

    def test_prompt_preserves_raw_without_silent_truncation(self):
        raw = "  пример\r\n"
        prompt = transcript.build_semantic_repair_prompt(raw, ["Обсуждаем контур"])
        data = json.loads(prompt.split("\n", 1)[1])
        self.assertEqual(data["raw_transcript"], raw)
        self.assertEqual(data["conversation_context"], ["Обсуждаем контур"])
        with self.assertRaises(ValueError):
            transcript.build_semantic_repair_prompt("x" * 8001)

    def test_prompt_context_is_bounded(self):
        prompt = transcript.build_semantic_repair_prompt("пример", ["x" * 1000] * 20)
        data = json.loads(prompt.split("\n", 1)[1])
        self.assertEqual(len(data["conversation_context"]), 8)
        self.assertTrue(all(len(line) == 800 for line in data["conversation_context"]))

    def test_invalid_raw_and_context_types_are_rejected(self):
        for raw in (None, b"text", 123):
            with self.assertRaises(TypeError):
                transcript.transcript_envelope(raw)
        for context in ("text", [None], 1):
            with self.assertRaises(TypeError):
                transcript.build_semantic_repair_prompt("text", context)

    def test_static_status_has_no_model_call(self):
        self.assertEqual(transcript.status(), {"ok": True, "module": "semantic_voice_transcript", "model_calls": 0})


if __name__ == "__main__":
    unittest.main()
