from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Scoreboard:
    wins: Dict[str, int] = field(default_factory=dict)

    def ensure_players(self, names: List[str]):
        for name in names:
            self.wins.setdefault(name, 0)

    def record_win(self, name: str):
        self.wins[name] = self.wins.get(name, 0) + 1

    def reset(self):
        for name in list(self.wins.keys()):
            self.wins[name] = 0

    def as_dict(self) -> Dict[str, int]:
        return dict(self.wins)

    def sorted_rows(self) -> List[Tuple[str, int]]:
        return sorted(self.wins.items(), key=lambda item: (-item[1], item[0]))

    def leader(self) -> Optional[Tuple[str, int]]:
        if not self.wins:
            return None
        top_score = max(self.wins.values())
        if top_score <= 0:
            return None
        leaders = [name for name, score in self.wins.items() if score == top_score]
        if len(leaders) != 1:
            return None
        return leaders[0], top_score
