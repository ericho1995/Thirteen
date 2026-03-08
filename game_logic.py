"""Thirteen Game - Rules & AI"""
from typing import List, Optional, Tuple
from enum import Enum
from cards import Card, ComboType, Hand

class GameState(Enum):
    PLAYER_TURN = "player_turn"
    AI_TURN = "ai_turn"
    PASSED = "passed"
    WINNER = "winner"

def get_combo_type(combo: List[Card]) -> ComboType:
    """Classify combo: single/pair/triple/straight."""
    if not combo:
        return ComboType.SINGLE
    
    values = sorted([c.value for c in combo])
    rank_counts = {}
    for c in combo:
        rank_counts[c.value] = rank_counts.get(c.value, 0) + 1
    
    # Quad > triple > pair > single
    if len(combo) == 4 and len(set(values)) == 1:
        return ComboType.QUAD
    if len(combo) == 3 and len(set(values)) == 1:
        return ComboType.TRIPLE
    if len(combo) == 2 and len(set(values)) == 1:
        return ComboType.PAIR
    if len(combo) == 1:
        return ComboType.SINGLE
    
    # Straight: consecutive, min length 3, no 2s
    if (len(set(values)) == len(combo) and 
        values[-1] - values[0] == len(combo) - 1 and 
        values[0] <= 14):  # No 2 start
        return ComboType.STRAIGHT
    
    return None  # Invalid

def is_valid_play(prev_combo: List[Card], play_combo: List[Card]) -> bool:
    """Can play beat previous?"""
    if not prev_combo:
        return True  # First play
    
    prev_type = get_combo_type(prev_combo)
    play_type = get_combo_type(play_combo)
    
    if not play_type or prev_type != play_type:
        return False
    
    if len(play_combo) != len(prev_combo):
        return False
    
    return play_combo[0].value > prev_combo[0].value

class AIPlayer:
    def __init__(self, difficulty: str = "medium"):
        self.difficulty = difficulty
    
    def choose_play(self, hand: Hand, prev_combo: List[Card]) -> List[Card]:
        """AI finds best valid play."""
        # Sort hand groups by size preference
        possible = self.find_valid_plays(hand.cards, prev_combo)
        if not possible:
            return []
        
        # Pick highest lead card
        best = max(possible, key=lambda c: c[0].value)
        return best
    
    def find_valid_plays(self, cards: List[Card], prev_combo: List[Card]) -> List[List[Card]]:
        """Find all valid combos from hand."""
        plays = []
        # Singles
        for card in cards:
            if is_valid_play(prev_combo, [card]):
                plays.append([card])
        # Pairs/Triples (simplified - check all combos)
        from itertools import combinations
        for size in [2, 3, 4]:
            for combo in combinations(cards, size):
                combo_list = list(combo)
                if is_valid_play(prev_combo, combo_list):
                    plays.append(combo_list)
        return plays
