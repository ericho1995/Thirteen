from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple, Dict, Any
from cards import Hand, Card
from history import HistoryLog
from scoreboard import Scoreboard


@dataclass
class GameState:
    hands: List[Hand] = field(default_factory=list)
    current_player: int = 0
    prev_combo: List[Card] = field(default_factory=list)
    selected: List[int] = field(default_factory=list)
    passed_players: Set[int] = field(default_factory=set)
    last_player_to_play: int = 0
    game_over: bool = False
    winner: Optional[str] = None
    previous_winner: Optional[int] = None
    must_open_with_three_spades: bool = False
    player_names: List[str] = field(default_factory=list)
    history: HistoryLog = field(default_factory=HistoryLog)
    scoreboard: Scoreboard = field(default_factory=Scoreboard)
    message: str = ""

    history_visible: bool = True
    history_width: int = 320
    history_height: int = 420
    history_pos: Tuple[int, int] = (1040, 170)
    history_scroll: int = 0
    dragging_history_resize: bool = False
    dragging_history_panel: bool = False
    history_drag_offset: Tuple[int, int] = (0, 0)

    active_animation: Optional[Dict[str, Any]] = None

    standings_visible: bool = True
    recent_plays_visible: bool = True
