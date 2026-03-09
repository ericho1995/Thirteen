from dataclasses import dataclass, field
from typing import List


@dataclass
class HistoryLog:
    entries: List[str] = field(default_factory=list)
    max_entries: int = 30

    def add(self, text: str):
        self.entries.append(text)
        self.entries = self.entries[-self.max_entries:]

    def clear(self):
        self.entries.clear()

    def recent(self, count: int = 12) -> List[str]:
        return self.entries[-count:]
