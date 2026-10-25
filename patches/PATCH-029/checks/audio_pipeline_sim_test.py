"""Deterministic smoke checks for the offline waveform/codec simulation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from audio_pipeline_sim import run, synthetic_speech_like_pcm


samples = synthetic_speech_like_pcm(seconds=2)
assert samples.dtype == "<i2" and len(samples) == 32000
first = samples.tobytes()
assert first == synthetic_speech_like_pcm(seconds=2).tobytes()

result = run(seconds=2)
rows = result["codec_variants"]
assert [row["name"] for row in rows] == [
    "pcm16", "zlib_pcm16_level_1", "zlib_pcm16_level_6", "zlib_pcm16_level_9", "mulaw8"]
assert rows[0]["ratio_vs_pcm"] == 1.0 and rows[0]["rmse_lsb"] == 0
assert all(row["bytes"] > 0 and row["encode_ms"] >= 0 and row["decode_ms"] >= 0 for row in rows)
assert all(row["ratio_vs_pcm"] > 0 for row in rows)
assert rows[-1]["ratio_vs_pcm"] < 1.0 and rows[-1]["rmse_lsb"] > 0
assert result["recognition"]["status"] == "NOT_RUN"
assert result["recognition"]["model_loaded"] is False
assert result["dialogue_fixture"]["automatic_speech_or_action"] is False
assert result["semantic_memory_preview"]["persisted"] is False
assert result["memory_write"] == "NOT_RUN_READ_ONLY_ADAPTER"
print("PASS: deterministic synthetic waveform and PCM/zlib/mu-law codec metrics")
print("PASS: ASR and semantic-memory writes remain explicitly unrun")
