from dataclasses import dataclass, field
from enum import Enum
import random
from typing import List
from config import SUIT_ORDER, RANK_ORDER


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
        return (self.value, self.suit_value)


    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"


@dataclass
class Deck:
    cards: List[Card] = field(default_factory=list)

    def __post_init__(self):
        if not self.cards:
            suits = ["♠", "♣", "♦", "♥"]
            ranks = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
            self.cards = [Card(rank, suit) for suit in suits for rank in ranks]

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

    def remove_card_objects(self, cards_to_remove: List[Card]):
        for card in cards_to_remove:
            self.cards.remove(card)
        self.sort_for_display()
