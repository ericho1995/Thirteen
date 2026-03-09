from dataclasses import dataclass, field
from enum import Enum
import random
from typing import Iterable, List
from config import SUIT_ORDER, RANK_ORDER, CARD_SUITS, CARD_RANKS


class ComboType(Enum):
    SINGLE = "single"
    PAIR = "pair"
    TRIPLE = "triple"
    QUAD = "quad"
    STRAIGHT = "straight"


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    @property
    def value(self) -> int:
        return RANK_ORDER[self.rank]

    @property
    def suit_value(self) -> int:
        return SUIT_ORDER[self.suit]

    def sort_key(self):
        return (self.value, self.suit_value)

    def display_sort_key(self):
        return self.sort_key()

    def is_three_of_spades(self) -> bool:
        return self.rank == "3" and self.suit == "♠"

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"


@dataclass
class Deck:
    cards: List[Card] = field(default_factory=list)

    def __post_init__(self):
        if not self.cards:
            self.cards = [Card(rank, suit) for suit in CARD_SUITS for rank in CARD_RANKS]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, count: int) -> List[Card]:
        dealt = self.cards[:count]
        self.cards = self.cards[count:]
        return dealt


@dataclass
class Hand:
    cards: List[Card]

    def sort_for_display(self):
        self.cards.sort(key=lambda c: c.display_sort_key())

    def remove_cards(self, indices: List[int]):
        for i in sorted(indices, reverse=True):
            del self.cards[i]
        self.sort_for_display()

    def remove_card_objects(self, cards_to_remove: Iterable[Card]):
        for card in cards_to_remove:
            self.cards.remove(card)
        self.sort_for_display()

    def contains_three_of_spades(self) -> bool:
        return any(card.is_three_of_spades() for card in self.cards)

    def is_empty(self) -> bool:
        return len(self.cards) == 0
