from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from cards import Hand, Card
from history import HistoryLog
from scoreboard import Scoreboard
from config import DEFAULT_PANEL_WIDTH, DEFAULT_PANEL_HEIGHT


@dataclass
class PanelState:
    visible: bool = True
    width: int = DEFAULT_PANEL_WIDTH
    height: int = DEFAULT_PANEL_HEIGHT
    pos: Tuple[int, int] = (0, 0)

    history_scroll: int = 0
    standings_scroll: int = 0

    dragging_resize: bool = False
    dragging_panel: bool = False
    drag_offset: Tuple[int, int] = (0, 0)

    dragging_history_scrollbar: bool = False
    dragging_standings_scrollbar: bool = False
    scrollbar_drag_offset_y: int = 0

    show_standings: bool = True
    show_history: bool = True



@dataclass
class DealState:
    in_progress: bool = False
    ready_to_deal: bool = True
    dealing_started: bool = False
    temp_deck: List[Card] = field(default_factory=list)
    deal_index: int = 0
    deal_timer: float = 0.0
    animated_card: Optional[Dict[str, Any]] = None


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
    active_animation: Optional[Dict[str, Any]] = None

    panel: PanelState = field(default_factory=PanelState)
    deal: DealState = field(default_factory=DealState)
