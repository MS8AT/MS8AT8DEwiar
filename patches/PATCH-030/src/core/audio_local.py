"""Локальный WAV и метаданные буфера. Модель, сеть и распознавание не вызываются."""
import base64
import io
import math
import os
from pathlib import Path
import tempfile
import wave

from audio_buffer import RATE


def wav_bytes(pcm):
    if not isinstance(pcm, bytes) or len(pcm) % 2 or not 0 < len(pcm) <= RATE * 2 * 300:
        raise ValueError("Нужен PCM16 mono не длиннее пяти минут")
    out = io.BytesIO()
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm)
    return out.getvalue()


def save_wav(path, pcm):
    """Готовый файл появляется атомарно; существующий файл никогда не заменяется."""
    path = Path(path)
    data = wav_bytes(pcm)
    if path.suffix.lower() != ".wav" or not path.parent.is_dir():
        raise ValueError("Выберите существующую папку и имя .wav")
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, suffix=".part", delete=False) as f:
            temp_path = Path(f.name)
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.link(temp_path, path)  # не перезаписывает даже при гонке с другим писателем
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    return {"bytes": len(data), "duration_s": len(pcm) / (RATE * 2)}


def status(host):
    capture = getattr(host, "capture", None)
    buffer = getattr(capture, "buffer", None)
    if buffer is None:
        return {"state": "unavailable", "history_enabled": False}
    raw = buffer.status()
    out = {"state": raw.get("state") if raw.get("state") in {"open", "closed"} else "unknown",
           "source": raw.get("source") if raw.get("source") in {"pc_mic", "wav", "synthetic"} else "unknown",
           "history_enabled": raw.get("history_enabled") is True and not bool(getattr(host, "muted", False))}
    for key in ("sample_rate", "frame_samples", "queue_frames", "queue_limit_ms", "queue_age_ms",
                "captured_frames", "captured_samples", "dropped_frames", "dropped_ms", "history_samples", "history_capacity_s"):
        value = raw.get(key)
        out[key] = value if type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 10**12 else None
    return out


def command(host, cmd, args):
    if not isinstance(args, dict):
        raise ValueError("Нужны параметры аудио")
    if cmd == "audio_buffer_status" and not args:
        return status(host)
    if cmd != "audio_history_export" or set(args) != {"confirm", "seconds"} or args["confirm"] is not True:
        raise ValueError("Сначала подтвердите сохранение истории звука")
    capture = getattr(host, "capture", None)
    if getattr(host, "muted", False) or getattr(capture, "buffer", None) is None:
        raise ValueError("История звука недоступна")
    pcm, metadata = capture.buffer.snapshot(args["seconds"])
    return {"filename": "dewiar-audio-history.wav", "wav_b64": base64.b64encode(wav_bytes(pcm)).decode("ascii"),
            "preview_only": True, **metadata}
