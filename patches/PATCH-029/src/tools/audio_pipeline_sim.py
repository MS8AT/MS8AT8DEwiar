"""Offline synthetic audio/codec benchmark; never opens a microphone or calls a model."""
import argparse
import json
import time

import numpy as np


RATE = 16000
SECONDS = 5
MU = 255.0


def synthetic_speech_like_pcm(rate=RATE, seconds=SECONDS):
    """Deterministic voiced harmonics with envelope and low synthetic noise."""
    if type(rate) is not int or rate < 8000 or rate > 48000:
        raise ValueError("rate must be an integer from 8000 to 48000")
    if type(seconds) is not int or not 1 <= seconds <= 30:
        raise ValueError("seconds must be an integer from 1 to 30")
    count = rate * seconds
    t = np.arange(count, dtype=np.float64) / rate
    # Repeating syllable-like envelope and slowly changing fundamental.
    envelope = (0.18 + 0.82 * np.maximum(0, np.sin(2 * np.pi * 2.4 * t)) ** 1.4)
    fundamental = 125 + 18 * np.sin(2 * np.pi * 0.23 * t)
    phase = 2 * np.pi * np.cumsum(fundamental) / rate
    signal = (0.48 * np.sin(phase) + 0.23 * np.sin(2 * phase + 0.4)
              + 0.12 * np.sin(3 * phase + 0.9) + 0.05 * np.sin(5 * phase))
    rng = np.random.default_rng(271828)
    signal = np.clip(signal * envelope + rng.normal(0, 0.003, count), -0.98, 0.98)
    return np.rint(signal * 32767).astype("<i2")


def _mulaw_encode(samples):
    normalized = np.asarray(samples, dtype=np.float64) / 32768.0
    magnitude = np.log1p(MU * np.abs(normalized)) / np.log1p(MU)
    companded = np.sign(normalized) * magnitude
    return np.rint((companded + 1.0) * 127.5).clip(0, 255).astype(np.uint8).tobytes()


def _mulaw_decode(data):
    values = np.frombuffer(data, dtype=np.uint8).astype(np.float64) / 127.5 - 1.0
    normalized = np.sign(values) * np.expm1(np.abs(values) * np.log1p(MU)) / MU
    return np.rint(normalized * 32768).clip(-32768, 32767).astype("<i2")


def _measure(name, source, encode, decode):
    start = time.perf_counter_ns()
    packed = encode(source)
    encode_ms = (time.perf_counter_ns() - start) / 1_000_000
    start = time.perf_counter_ns()
    restored = decode(packed)
    decode_ms = (time.perf_counter_ns() - start) / 1_000_000
    restored = np.asarray(restored, dtype="<i2")
    if restored.shape != source.shape:
        raise ValueError(f"{name}: decoded sample count changed")
    diff = source.astype(np.int32) - restored.astype(np.int32)
    return {"name": name, "bytes": len(packed),
            "ratio_vs_pcm": round(len(packed) / source.nbytes, 5),
            "encode_ms": round(encode_ms, 3), "decode_ms": round(decode_ms, 3),
            "rmse_lsb": round(float(np.sqrt(np.mean(diff.astype(np.float64) ** 2))), 2),
            "max_abs_error_lsb": int(np.max(np.abs(diff)))}


def run(seconds=SECONDS):
    source = synthetic_speech_like_pcm(seconds=seconds)
    raw = source.tobytes()
    import zlib
    variants = [
        _measure("pcm16", source, lambda samples: samples.tobytes(), lambda data: np.frombuffer(data, dtype="<i2")),
        *[_measure(f"zlib_pcm16_level_{level}", source,
                   lambda samples, level=level: zlib.compress(samples.tobytes(), level),
                   lambda data: np.frombuffer(zlib.decompress(data), dtype="<i2"))
          for level in (1, 6, 9)],
        _measure("mulaw8", source, _mulaw_encode, _mulaw_decode),
    ]
    # ASR and semantic-memory integrations are represented as explicit gates.
    # The fixture text exercises context shaping only; it is not recognition output.
    fixture_turns = [
        {"role": "user", "text": "Сравни размер, скорость и качество сжатия речи."},
        {"role": "user", "text": "Нужен короткий вывод и следующий вопрос к 18:00."},
    ]
    context = " ".join(turn["text"] for turn in fixture_turns)[-600:]
    memory_preview = {"scope": {"kind": "task", "id": "synthetic-audio-benchmark"},
                      "content": "Сравнить размер, скорость и качество; нужен короткий вывод к 18:00.",
                      "persisted": False, "write_status": "not_supported_read_only_memory"}
    return {"simulation": "synthetic_speech_like_wave", "sample_rate": RATE,
            "channels": 1, "duration_seconds": seconds, "input_bytes_pcm16": len(raw),
            "codec_variants": variants,
            "recognition": {"status": "NOT_RUN", "model_loaded": False,
                            "reason": "No ASR/model inference in offline simulation"},
            "dialogue_fixture": {"status": "synthetic_context_only", "context_chars": len(context),
                                 "short_answer": "Подготовлю сравнение по трём метрикам.",
                                 "timely_question_suggestion": "Что важнее для выбора: скорость, размер или точность?",
                                 "automatic_speech_or_action": False},
            "semantic_memory_preview": memory_preview,
            "memory_write": "NOT_RUN_READ_ONLY_ADAPTER",
            "claim_boundary": "Codec numbers are synthetic local measurements; ASR quality and real-time latency are not measured."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=int, default=SECONDS)
    args = parser.parse_args()
    print(json.dumps(run(args.seconds), ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
