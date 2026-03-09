from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Scoreboard:
    wins: Dict[str, int] = field(default_factory=dict)

    def ensure_players(self, names: List[str]):
        for name in names:
            self.wins.setdefault(name, 0)

    def record_win(self, name: str):
        self.wins[name] = self.wins.get(name, 0) + 1

    def as_dict(self) -> Dict[str, int]:
        return dict(self.wins)
