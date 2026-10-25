"""Кадры микрофона/WAV: короткая очередь и отдельная история в памяти.

В callback только копирование PCM, метки и ограниченные deque под коротким замком.
Здесь нет модели, диска, сети или ожидания свободного места. Это не hard realtime.
"""
from collections import deque
from dataclasses import dataclass
import math
import queue
import threading
import time
import uuid

RATE, FRAME = 16000, 512
SOURCES = {"pc_mic", "wav", "synthetic"}


def validate_options(history_seconds=10, queue_ms=480, history_enabled=False):
    if type(history_seconds) is not int or not 1 <= history_seconds <= 30:
        raise ValueError("История звука: от 1 до 30 секунд")
    if type(queue_ms) is not int or not 32 <= queue_ms <= 2000:
        raise ValueError("Очередь звука: от 32 до 2000 мс")
    if type(history_enabled) is not bool:
        raise ValueError("История звука: включена или выключена")


@dataclass(frozen=True)
class AudioFrame:
    pcm: bytes
    sequence: int
    start_sample: int
    captured_at: float
    source: str
    stream_id: str

    @property
    def samples(self):
        return len(self.pcm) // 2


class AudioBuffer:
    """Один producer, несколько последовательных consumers; snapshot не съедает очередь."""

    def __init__(self, source="pc_mic", history_seconds=10, queue_ms=480,
                 history_enabled=False, clock=time.monotonic):
        validate_options(history_seconds, queue_ms, history_enabled)
        if source not in SOURCES:
            raise ValueError("Неизвестный источник звука")
        self.source, self.clock = source, clock
        self.stream_id = uuid.uuid4().hex
        self.capacity_samples = history_seconds * RATE
        self.queue_capacity = max(1, queue_ms * RATE // (1000 * FRAME))
        self.history_enabled = history_enabled
        self._condition = threading.Condition()
        self._queue, self._history = deque(), deque()
        self._history_samples = 0
        self._sequence = self._samples = 0
        self.dropped_frames = self.dropped_samples = 0
        self._closed = False
        self._short_frame = False

    def push(self, pcm):
        if not isinstance(pcm, bytes) or not pcm or len(pcm) % 2 or len(pcm) > FRAME * 2:
            raise ValueError("Кадр: PCM16 mono, от 1 до 512 samples")
        now = self.clock()
        if not math.isfinite(now):
            raise ValueError("Некорректное время кадра")
        with self._condition:
            if self._closed:
                return None
            if self._short_frame:
                raise ValueError("После последнего неполного кадра нужен новый поток")
            frame = AudioFrame(pcm, self._sequence, self._samples, now, self.source, self.stream_id)
            self._sequence += 1
            self._samples += frame.samples
            self._short_frame = frame.samples < FRAME
            if len(self._queue) == self.queue_capacity:
                old = self._queue.popleft()
                self.dropped_frames += 1
                self.dropped_samples += old.samples
            self._queue.append(frame)
            if self.history_enabled:
                self._history.append(frame)
                self._history_samples += frame.samples
                # Сохраняем граничный кадр целиком; обрезаем его только при snapshot.
                while self._history and self._history_samples - self._history[0].samples >= self.capacity_samples:
                    self._history_samples -= self._history.popleft().samples
            self._condition.notify()
            return frame

    def get(self, timeout=2):
        with self._condition:
            if not self._condition.wait_for(lambda: self._queue or self._closed, timeout):
                raise queue.Empty
            if not self._queue:
                raise queue.Empty
            return self._queue.popleft()

    def enable_history(self, enabled):
        if type(enabled) is not bool:
            raise ValueError("История звука: да/нет")
        with self._condition:
            if enabled != self.history_enabled or not enabled:
                self._history.clear()
                self._history_samples = 0
            self.history_enabled = enabled and not self._closed

    def snapshot(self, seconds=10):
        if type(seconds) not in (int, float) or not math.isfinite(seconds) or not 0 < seconds <= self.capacity_samples / RATE:
            raise ValueError("Длительность за пределами истории")
        count = int(seconds * RATE)
        if count < 1:
            raise ValueError("История должна содержать хотя бы один sample")
        with self._condition:
            if not self.history_enabled or self._closed:
                raise ValueError("История звука выключена")
            frames = tuple(self._history)
            end = self._samples
        if not frames:
            raise ValueError("История звука пока пуста")
        data = b"".join(frame.pcm for frame in frames)[-count * 2:]
        return data, {"source": self.source, "stream_id": self.stream_id,
                      "start_sample": end - len(data) // 2, "end_sample": end,
                      "sample_rate": RATE, "channels": 1, "duration_s": len(data) / (2 * RATE)}

    def status(self):
        with self._condition:
            oldest = self._queue[0].captured_at if self._queue else None
            return {"state": "closed" if self._closed else "open", "source": self.source,
                    "sample_rate": RATE, "frame_samples": FRAME,
                    "queue_frames": len(self._queue), "queue_limit_ms": self.queue_capacity * FRAME * 1000 / RATE,
                    "queue_age_ms": max(0, (self.clock() - oldest) * 1000) if oldest is not None else 0,
                    "captured_frames": self._sequence, "captured_samples": self._samples,
                    "dropped_frames": self.dropped_frames, "dropped_ms": self.dropped_samples * 1000 / RATE,
                    "history_enabled": self.history_enabled,
                    "history_samples": min(self.capacity_samples, self._history_samples),
                    "history_capacity_s": self.capacity_samples / RATE}

    def close(self):
        with self._condition:
            self._closed = True
            self.history_enabled = False
            self._queue.clear()
            self._history.clear()
            self._history_samples = 0
            self._condition.notify_all()
