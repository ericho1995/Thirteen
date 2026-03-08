"""Thirteen Game - Rules & AI"""
from typing import List, Optional
from enum import Enum
from itertools import combinations
from cards import Card, ComboType, Hand


class GameState(Enum):
    PLAYER_TURN = "player_turn"
    AI_TURN = "ai_turn"
    PASSED = "passed"
    WINNER = "winner"


def sorted_combo(combo: List[Card]) -> List[Card]:
    return sorted(combo, key=lambda c: c.value)


def get_combo_type(combo: List[Card]) -> Optional[ComboType]:
    if not combo:
        return None

    combo = sorted_combo(combo)
    values = [c.value for c in combo]

    if len(combo) == 1:
        return ComboType.SINGLE

    if len(set(values)) == 1:
        if len(combo) == 2:
            return ComboType.PAIR
        if len(combo) == 3:
            return ComboType.TRIPLE
        if len(combo) == 4:
            return ComboType.QUAD

    if len(combo) >= 3:
        if 15 in values:
            return None
        if len(set(values)) == len(values) and all(values[i] + 1 == values[i + 1] for i in range(len(values) - 1)):
            return ComboType.STRAIGHT

    return None


def combo_rank(combo: List[Card]) -> int:
    combo = sorted_combo(combo)
    return combo[-1].value


def is_valid_play(prev_combo: List[Card], play_combo: List[Card]) -> bool:
    play_type = get_combo_type(play_combo)
    if play_type is None:
        return False

    if not prev_combo:
        return True

    prev_type = get_combo_type(prev_combo)
    if prev_type is None:
        return False

    if play_type != prev_type:
        return False

    if len(play_combo) != len(prev_combo):
        return False

    return combo_rank(play_combo) > combo_rank(prev_combo)


class AIPlayer:
    def __init__(self, difficulty: str = "medium"):
        self.difficulty = difficulty

    def choose_play(self, hand: Hand, prev_combo: List[Card]) -> List[Card]:
        possible = self.find_valid_plays(hand.cards, prev_combo)
        if not possible:
            return []

        return min(possible, key=combo_rank)

    def find_valid_plays(self, cards: List[Card], prev_combo: List[Card]) -> List[List[Card]]:
        plays = []

        max_size = min(5, len(cards))
        for size in range(1, max_size + 1):
            for combo in combinations(cards, size):
                combo_list = list(combo)
                if is_valid_play(prev_combo, combo_list):
                    plays.append(sorted_combo(combo_list))

        return plays
