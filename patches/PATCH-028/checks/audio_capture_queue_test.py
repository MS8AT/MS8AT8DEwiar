"""Проверяет ограниченную очередь кадров без доступа к микрофону."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
from audio_queue import LatestFrameQueue


q = LatestFrameQueue(max_frames=3)
for frame in (b"a", b"b", b"c", b"d", b"e"):
    assert q.put_latest(frame) is True
assert q.qsize() == 3
assert q.dropped_frames == 2
assert [q.get(), q.get(), q.get()] == [b"c", b"d", b"e"]
print("PASS: bounded queue drops stale frames and delivers latest in order")

try:
    LatestFrameQueue(max_frames=0)
except ValueError:
    pass
else:
    raise AssertionError("zero capacity accepted")
print("PASS: invalid queue capacity rejected")
