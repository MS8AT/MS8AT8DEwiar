"""Проверяет WAV-приём на памяти и фиктивном распознавателе, без микрофона и сети."""
import io
import re
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.audio_ingest import AudioFileError, MAX_FILE_BYTES, TARGET_RATE, transcribe_wav, wav_to_pcm


def wav_bytes(rate=16000, channels=1, frames=None):
    frames = frames if frames is not None else rate // 2
    out = io.BytesIO()
    with wave.open(out, "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(b"\x01\x00" * frames * channels)
    return out.getvalue()


class FakeSTT:
    name = "mock-local"

    def __init__(self):
        self.calls = []

    def transcribe(self, pcm):
        self.calls.append(pcm)
        return "hello world" if len(self.calls) == 1 else "world again"


class Host:
    def __init__(self, stt):
        self.stt = stt

    def current_stt(self):
        return self.stt


def expect_error(fn, contains):
    try:
        fn()
    except AudioFileError as exc:
        assert contains in str(exc), str(exc)
    else:
        raise AssertionError("expected AudioFileError")


pcm, duration = wav_to_pcm(wav_bytes(8000, 2))
assert len(pcm) == TARGET_RATE and duration == 0.5
print("PASS: stereo 8 kHz becomes mono 16 kHz PCM")

expect_error(lambda: wav_to_pcm(b"not a wav"), "прочитать")
expect_error(lambda: wav_to_pcm(wav_bytes(rate=16000, frames=16000 * 301)), "5 минут")
expect_error(lambda: wav_to_pcm(b"0" * (MAX_FILE_BYTES + 1)), "10 МБ")
print("PASS: malformed, too-long and oversized inputs rejected")

stt = FakeSTT()
result = transcribe_wav(Host(stt), wav_bytes(rate=16000, frames=16000 * 25))
assert len(stt.calls) == 2
assert result["text"] == "hello world again", result["text"]
assert result["preview_only"] is True and result["backend"] == "mock-local"
assert result["segments"][0]["start"] == 0 and result["segments"][1]["start"] == 19.75
print("PASS: chunks use 250 ms overlap, deduplicate boundary words and return preview-only text")

try:
    transcribe_wav(Host(None), wav_bytes())
except AudioFileError as exc:
    assert "загружается" in str(exc)
else:
    raise AssertionError("missing recognizer was accepted")
print("PASS: unavailable recognizer fails clearly")

print("PARTIAL: app UI/command wiring is checked only in the full integration tree")
