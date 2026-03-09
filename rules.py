from itertools import combinations
from typing import List, Optional
from cards import Card, ComboType


def card_sort_key(card: Card):
    return card.sort_key()


def display_sort_key(card: Card):
    return card.display_sort_key()


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
        is_run = len(set(values)) == len(values) and all(
            values[i] + 1 == values[i + 1] for i in range(len(values) - 1)
        )
        if is_run:
            return ComboType.STRAIGHT

    return None


def combo_rank(combo: List[Card]):
    combo = sorted_combo(combo)
    combo_type = get_combo_type(combo)

    if combo_type == ComboType.SINGLE:
        c = combo[0]
        return (c.value, c.suit_value)

    if combo_type in {ComboType.PAIR, ComboType.TRIPLE, ComboType.QUAD}:
        return (combo[0].value, max(card.suit_value for card in combo))

    if combo_type == ComboType.STRAIGHT:
        high = combo[-1]
        return (high.value, high.suit_value, len(combo))

    return (-1, -1, -1)


def combo_contains_three_spades(combo: List[Card]) -> bool:
    return any(card.is_three_of_spades() for card in combo)


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
    grouped = {}

    for card in sorted(cards, key=card_sort_key):
        if card.value == 15:
            continue
        grouped.setdefault(card.value, []).append(card)

    values = sorted(grouped.keys())

    for size in range(min_length, max_length + 1):
        for i in range(len(values) - size + 1):
            run = values[i:i + size]
            if all(run[j] + 1 == run[j + 1] for j in range(len(run) - 1)):
                chosen = [sorted(grouped[v], key=card_sort_key)[0] for v in run]
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
