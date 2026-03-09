"""Thirteen Game - Rules & AI"""
from typing import List, Optional
from enum import Enum
from itertools import combinations
from cards import Card, ComboType, Hand

SUIT_ORDER = {"♠": 1, "♣": 2, "♦": 3, "♥": 4}


class GameState(Enum):
    PLAYER_TURN = "player_turn"
    AI_TURN = "ai_turn"
    PASSED = "passed"
    WINNER = "winner"


def card_sort_key(card: Card):
    return (card.value, SUIT_ORDER.get(card.suit, 0))


def display_sort_key(card: Card):
    return (-card.value, -SUIT_ORDER.get(card.suit, 0))


def sorted_combo(combo: List[Card]) -> List[Card]:
    return sorted(combo, key=card_sort_key)


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


def combo_rank(combo: List[Card]):
    combo = sorted_combo(combo)
    combo_type = get_combo_type(combo)

    if combo_type == ComboType.SINGLE:
        c = combo[0]
        return (c.value, SUIT_ORDER[c.suit])

    if combo_type in {ComboType.PAIR, ComboType.TRIPLE, ComboType.QUAD}:
        highest_suit = max(SUIT_ORDER[c.suit] for c in combo)
        return (combo[0].value, highest_suit)

    if combo_type == ComboType.STRAIGHT:
        high = combo[-1]
        return (high.value, SUIT_ORDER[high.suit], len(combo))

    return (-1, -1)


def combo_contains_three_spades(combo: List[Card]) -> bool:
    return any(card.rank == "3" and card.suit == "♠" for card in combo)


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


def find_pairs(cards: List[Card]) -> List[List[Card]]:
    return [sorted_combo(list(c)) for c in combinations(cards, 2) if get_combo_type(list(c)) == ComboType.PAIR]


def find_triples(cards: List[Card]) -> List[List[Card]]:
    return [sorted_combo(list(c)) for c in combinations(cards, 3) if get_combo_type(list(c)) == ComboType.TRIPLE]


def find_quads(cards: List[Card]) -> List[List[Card]]:
    return [sorted_combo(list(c)) for c in combinations(cards, 4) if get_combo_type(list(c)) == ComboType.QUAD]


def find_straights(cards: List[Card], min_length: int = 3, max_length: int = 6) -> List[List[Card]]:
    straights = []
    unique_cards = {}

    for card in sorted(cards, key=card_sort_key):
        if card.value == 15:
            continue
        if card.value not in unique_cards:
            unique_cards[card.value] = []
        unique_cards[card.value].append(card)

    unique_values = sorted(unique_cards.keys())

    for size in range(min_length, max_length + 1):
        for i in range(len(unique_values) - size + 1):
            run = unique_values[i:i + size]
            if all(run[j] + 1 == run[j + 1] for j in range(len(run) - 1)):
                chosen = []
                for value in run:
                    chosen.append(sorted(unique_cards[value], key=lambda c: SUIT_ORDER[c.suit])[0])
                if get_combo_type(chosen) == ComboType.STRAIGHT:
                    straights.append(sorted_combo(chosen))

    return straights


def generate_all_valid_combos(cards: List[Card]) -> List[List[Card]]:
    singles = [[card] for card in sorted(cards, key=card_sort_key)]
    pairs = find_pairs(cards)
    triples = find_triples(cards)
    quads = find_quads(cards)
    straights = find_straights(cards)

    all_combos = singles + pairs + triples + quads + straights

    deduped = []
    seen = set()
    for combo in all_combos:
        key = tuple((c.rank, c.suit) for c in combo)
        if key not in seen:
            seen.add(key)
            deduped.append(combo)
    return deduped


class AIPlayer:
    def __init__(self, difficulty: str = "medium"):
        self.difficulty = difficulty

    def lead_sort_key(self, combo: List[Card]):
        combo_type = get_combo_type(combo)
        type_priority = {
            ComboType.SINGLE: 0,
            ComboType.PAIR: 1,
            ComboType.TRIPLE: 2,
            ComboType.STRAIGHT: 3,
            ComboType.QUAD: 4,
        }.get(combo_type, 99)
        return (type_priority, len(combo), combo_rank(combo))

    def response_sort_key(self, combo: List[Card]):
        return (combo_rank(combo), len(combo))

    def choose_play(
        self,
        hand: Hand,
        prev_combo: List[Card],
        must_contain_three_spades: bool = False
    ) -> List[Card]:
        possible = self.find_valid_plays(hand.cards, prev_combo)

        if must_contain_three_spades:
            possible = [combo for combo in possible if combo_contains_three_spades(combo)]

        if not possible:
            return []

        if not prev_combo:
            possible.sort(key=self.lead_sort_key)
            return possible[0]

        possible.sort(key=self.response_sort_key)
        return possible[0]

    def find_valid_plays(self, cards: List[Card], prev_combo: List[Card]) -> List[List[Card]]:
        all_combos = generate_all_valid_combos(cards)
        return [combo for combo in all_combos if is_valid_play(prev_combo, combo)]
