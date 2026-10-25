import io
import queue
import threading
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
from audio_buffer import AudioBuffer, FRAME, RATE
from audio_context import ContextPreparation
import audio_local
class BufferTests(unittest.TestCase):
    def test_ten_second_ring_is_exact_after_wrap_and_queue_loss(self):
        b = AudioBuffer(source="synthetic", history_enabled=True)
        data = b"".join((i % 32768).to_bytes(2, "little") for i in range(12 * RATE + 123))
        for start in range(0, len(data), FRAME * 2):
            b.push(data[start:start + FRAME * 2])
        pcm, info = b.snapshot(10)
        self.assertEqual(pcm, data[-10 * RATE * 2:])
        self.assertEqual(info["start_sample"], len(data) // 2 - 10 * RATE)
        self.assertEqual(info["end_sample"], len(data) // 2)
        status = b.status()
        self.assertEqual(status["queue_frames"], 15)
        self.assertEqual(status["queue_limit_ms"], 480)
        self.assertEqual(status["dropped_frames"], status["captured_frames"] - 15)
        self.assertEqual(status["dropped_ms"], status["dropped_frames"] * 32)
        frame = b.get()
        self.assertEqual(frame.sequence, status["dropped_frames"])
        self.assertEqual(frame.start_sample, frame.sequence * FRAME)
        self.assertEqual(frame.source, "synthetic")

    def test_closed_buffer_wakes_waiter_and_clears_audio(self):
        b = AudioBuffer(history_enabled=True)
        started, stopped = threading.Event(), threading.Event()
        def wait():
            started.set()
            try: b.get(timeout=2)
            except queue.Empty: stopped.set()
        t = threading.Thread(target=wait); t.start(); self.assertTrue(started.wait(1))
        b.close(); t.join(1)
        self.assertTrue(stopped.is_set())
        self.assertIsNone(b.push(b"\0" * 1024))
        self.assertEqual(b.status()["history_samples"], 0)
        with self.assertRaises(ValueError): b.snapshot()

    def test_history_off_and_invalid_format_fail_closed(self):
        b = AudioBuffer()
        b.push(b"\0" * 1024)
        self.assertEqual(b.status()["history_samples"], 0)
        with self.assertRaises(ValueError): b.snapshot()
        for pcm in (b"", b"x", b"x" * 1026, "not bytes"):
            with self.assertRaises(ValueError): b.push(pcm)
        b.enable_history(True); b.push(b"\0" * 1024)
        for seconds in (True, 0, float("nan"), 1e-9, 11):
            with self.assertRaises(ValueError): b.snapshot(seconds)
        b.enable_history(False)
        self.assertEqual(b.status()["history_samples"], 0)

    def test_queue_age_uses_capture_clock(self):
        now = [100.0]
        b = AudioBuffer(clock=lambda: now[0])
        b.push(b"\0" * 1024); now[0] = 100.25
        self.assertEqual(b.status()["queue_age_ms"], 250)

class ContextTests(unittest.TestCase):
    def test_revised_phrase_cancels_old_recall(self):
        now = [0.0]; c = ContextPreparation(clock=lambda: now[0])
        c.update("Выключи сейчас весь свет"); self.assertIsNone(c.request())
        now[0] = .6; old = c.request(); self.assertIsNotNone(old)
        c.update("Выключи свет в игре, дома не трогай", final=True)
        self.assertFalse(c.accept(old, ["Дом: выключатель"]))
        self.assertEqual(c.context()["memory"], "")
        new = c.request(); self.assertTrue(c.accept(new, ["Игра: горячая клавиша"]))
        self.assertEqual(c.context()["memory"], "Игра: горячая клавиша")
        self.assertFalse(c.context()["memory_write"])

    def test_same_final_uses_prepared_context_then_expires(self):
        now = [0.0]; c = ContextPreparation(clock=lambda: now[0])
        c.update("Расскажи про микрофон Лиры"); now[0] = .6
        ticket = c.request(); self.assertTrue(c.accept(ticket, ["Настройки звука"]))
        self.assertFalse(c.context()["ready"])
        c.update(ticket.query, final=True)
        self.assertEqual(c.context()["memory"], "Настройки звука")
        now[0] = 5; self.assertEqual(c.context()["memory"], ""); self.assertIsNone(c.request())

    def test_budget_deadline_and_cross_session(self):
        now = [0.0]; c = ContextPreparation(clock=lambda: now[0]); c.update("один два три", final=True)
        ticket = c.request()
        other = ContextPreparation(); other.update("один два три", final=True)
        self.assertFalse(c.accept(other.request(), ["foreign"]))
        with self.assertRaises(ValueError): c.accept(ticket, ["x" * 6001])
        now[0] = 4; self.assertFalse(c.accept(ticket, ["late"])); self.assertIsNone(c.request())

if __name__ == "__main__": unittest.main()
