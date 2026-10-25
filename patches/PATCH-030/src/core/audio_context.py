"""Версии текста для предварительного recall. Сам модуль не вызывает модель или память.

Внешний исполнитель получает запрос с ticket; ответ принимается только пока
совпадают session/revision/query и срок. Черновики живут в RAM и не выполняют команды.
"""
from dataclasses import dataclass
import math
import time
import uuid


@dataclass(frozen=True)
class RecallTicket:
    session: str
    revision: int
    query: str
    issued_at: float


class ContextPreparation:
    def __init__(self, clock=time.monotonic, stable_ms=500, ttl_ms=3000, max_chars=6000):
        if type(stable_ms) is not int or not 100 <= stable_ms <= 5000:
            raise ValueError("stable_ms: 100–5000")
        if type(ttl_ms) is not int or not stable_ms <= ttl_ms <= 30000:
            raise ValueError("ttl_ms: stable_ms–30000")
        if type(max_chars) is not int or not 200 <= max_chars <= 12000:
            raise ValueError("max_chars: 200–12000")
        self.clock, self.stable_s, self.ttl_s, self.max_chars = clock, stable_ms / 1000, ttl_ms / 1000, max_chars
        self.session = uuid.uuid4().hex
        self.revision, self.text, self.final = 0, "", False
        self.changed_at = clock()
        self.pending = None
        self.prepared = None
        self.requested_revision = -1
        self.cancelled = self.stale_results = 0

    def update(self, text, final=False):
        if not isinstance(text, str) or len(text) > self.max_chars or type(final) is not bool:
            raise ValueError("Некорректная версия текста")
        if text == self.text and final and not self.final:
            self.final = True  # прежний recall применим: подтверждены ровно те же слова
            return self.revision
        if text != self.text or final != self.final:
            if self.pending or self.prepared:
                self.cancelled += 1
            self.revision += 1
            self.text, self.final, self.changed_at = text, final, self.clock()
            self.pending = self.prepared = None
        return self.revision

    def request(self):
        now = self.clock()
        if (not math.isfinite(now) or len(self.text.split()) < 3 or self.pending or self.prepared
                or self.requested_revision == self.revision):
            return None
        if not self.final and now - self.changed_at < self.stable_s:
            return None
        self.pending = RecallTicket(self.session, self.revision, self.text, now)
        self.requested_revision = self.revision
        return self.pending

    def accept(self, ticket, fragments):
        if not isinstance(ticket, RecallTicket) or ticket != self.pending or self.clock() - ticket.issued_at > self.ttl_s:
            self.stale_results += 1
            if ticket == self.pending:
                self.pending = None
            return False
        if not isinstance(fragments, list) or len(fragments) > 5 or any(not isinstance(s, str) for s in fragments):
            raise ValueError("Recall: не более пяти текстовых фрагментов")
        text = "\n".join(fragments)
        if len(text) > self.max_chars:
            raise ValueError("Recall превысил бюджет символов")
        self.prepared, self.pending = (ticket, text), None
        return True

    def context(self):
        # Нефинальный текст можно использовать лишь как запрос к read-only recall.
        if not self.final:
            return {"ready": False, "revision": self.revision, "memory": ""}
        if self.prepared and self.clock() - self.prepared[0].issued_at > self.ttl_s:
            self.prepared = None
        return {"ready": True, "revision": self.revision, "transcript": self.text,
                "memory": self.prepared[1] if self.prepared else "", "memory_write": False}
