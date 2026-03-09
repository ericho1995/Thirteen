from typing import Any, Dict, List
from cards import Hand, Card, ComboType
from rules import (
    get_combo_type,
    combo_rank,
    combo_contains_three_spades,
    generate_all_valid_combos,
    is_valid_play,
    find_pairs,
    find_triples,
    find_quads,
    find_straights,
)


class AIPlayer:
    def __init__(self, difficulty: str = "expert"):
        self.difficulty = difficulty

    def choose_play(
        self,
        hand: Hand,
        prev_combo: List[Card],
        must_contain_three_spades: bool = False
    ) -> List[Card]:
        legal = self.find_legal_plays(hand, prev_combo, must_contain_three_spades)
        if not legal:
            return []

        scored = []
        for combo in legal:
            score = self.score_move(hand, combo, prev_combo, must_contain_three_spades)
            scored.append((score, combo))

        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[0][1]

    def find_legal_plays(
        self,
        hand: Hand,
        prev_combo: List[Card],
        must_contain_three_spades: bool = False
    ) -> List[List[Card]]:
        combos = generate_all_valid_combos(hand.cards)
        legal = [combo for combo in combos if is_valid_play(prev_combo, combo)]

        if must_contain_three_spades:
            legal = [combo for combo in legal if combo_contains_three_spades(combo)]

        return legal

    def score_move(
        self,
        hand: Hand,
        combo: List[Card],
        prev_combo: List[Card],
        must_contain_three_spades: bool = False
    ) -> float:
        combo_type = get_combo_type(combo)
        before = self.evaluate_hand(hand.cards)
        remaining_cards = hand.cards[:]
        for card in combo:
            remaining_cards.remove(card)
        after = self.evaluate_hand(remaining_cards)

        score = 0.0
        score += (after["structure_score"] - before["structure_score"]) * 8.0
        score -= after["dead_high_cards"] * 1.2
        score -= after["singles"] * 0.9

        score += len(combo) * 2.5
        score += (13 - len(remaining_cards)) * 0.15

        if len(remaining_cards) <= 4:
            score += len(combo) * 4.0
            score -= after["dead_high_cards"] * 0.5

        combo_strength = self.normalized_strength(combo)
        score += combo_strength * 1.5

        if not prev_combo:
            score += self.lead_bonus(combo, before, after)
        else:
            score += self.response_bonus(combo, prev_combo)

        if combo_type == ComboType.QUAD and len(remaining_cards) > 4:
            score -= 8.0

        if combo_type == ComboType.SINGLE and combo[0].value >= 14 and len(remaining_cards) > 4:
            score -= 5.0

        if combo_type == ComboType.PAIR and combo[0].value >= 14 and len(remaining_cards) > 4:
            score -= 4.0

        if must_contain_three_spades:
            score += 3.0
            if combo_type == ComboType.SINGLE:
                score -= 1.5

        if len(remaining_cards) == 0:
            score += 1000.0

        return score

    def evaluate_hand(self, cards: List[Card]) -> Dict[str, Any]:
        pairs = find_pairs(cards)
        triples = find_triples(cards)
        quads = find_quads(cards)
        straights = find_straights(cards, 3, 6)

        used_in_pairs = {card for combo in pairs for card in combo}
        used_in_triples = {card for combo in triples for card in combo}
        used_in_straights = {card for combo in straights for card in combo}

        singles = []
        dead_high_cards = 0
        flexible_cards = 0

        for card in cards:
            in_structure = card in used_in_pairs or card in used_in_triples or card in used_in_straights
            if not in_structure:
                singles.append(card)
                if card.value >= 14:
                    dead_high_cards += 1
            else:
                flexible_cards += 1

        structure_score = (
            len(straights) * 4.5 +
            len(triples) * 3.2 +
            len(pairs) * 2.2 +
            len(quads) * 5.5 +
            flexible_cards * 0.35
        )

        return {
            "pairs": len(pairs),
            "triples": len(triples),
            "quads": len(quads),
            "straights": len(straights),
            "singles": len(singles),
            "dead_high_cards": dead_high_cards,
            "structure_score": structure_score,
        }

    def normalized_strength(self, combo: List[Card]) -> float:
        rank = combo_rank(combo)
        combo_type = get_combo_type(combo)

        if combo_type in {ComboType.SINGLE, ComboType.PAIR, ComboType.TRIPLE, ComboType.QUAD}:
            return rank[0] + rank[1] * 0.1
        if combo_type == ComboType.STRAIGHT:
            return rank[0] + rank[1] * 0.1 + rank[2] * 0.3
        return 0.0

    def lead_bonus(self, combo: List[Card], before: Dict[str, Any], after: Dict[str, Any]) -> float:
        combo_type = get_combo_type(combo)
        score = 0.0

        if combo_type == ComboType.STRAIGHT:
            score += 7.0
        elif combo_type == ComboType.TRIPLE:
            score += 4.5
        elif combo_type == ComboType.PAIR:
            score += 3.0
        elif combo_type == ComboType.SINGLE:
            score -= 1.5
        elif combo_type == ComboType.QUAD:
            score -= 6.0

        if after["singles"] < before["singles"]:
            score += 2.0

        return score

    def response_bonus(self, combo: List[Card], prev_combo: List[Card]) -> float:
        score = 0.0
        my_strength = self.normalized_strength(combo)
        target_strength = self.normalized_strength(prev_combo)
        margin = my_strength - target_strength

        score -= margin * 0.8

        combo_type = get_combo_type(combo)
        if combo_type == ComboType.QUAD:
            score -= 5.0

        return score
