"""Thirteen Game - Cards Module"""
from typing import List
from dataclasses import dataclass
from enum import Enum
import random


RANKS = ['3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A', '2']
SUITS = ['♠', '♥', '♦', '♣']
VALUES = {r: i + 3 for i, r in enumerate(RANKS)}


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str
    value: int

    def __str__(self):
        return f"{self.rank}{self.suit}"

    def __repr__(self):
        return self.__str__()


class ComboType(Enum):
    SINGLE = "single"
    PAIR = "pair"
    TRIPLE = "triple"
    QUAD = "quad"
    STRAIGHT = "straight"


class Deck:
    def __init__(self):
        self.cards: List[Card] = []
        self.build_deck()

    def build_deck(self):
        self.cards = [Card(r, s, VALUES[r]) for r in RANKS for s in SUITS]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num: int) -> List[Card]:
        if num > len(self.cards):
            raise ValueError(f"Not enough cards left to deal {num}")
        return [self.cards.pop() for _ in range(num)]


class Hand:
    def __init__(self, cards: List[Card]):
        self.cards = sorted(cards, key=lambda c: c.value)

    def __len__(self):
        return len(self.cards)

    def is_empty(self):
        return len(self.cards) == 0

    def sort(self):
        self.cards.sort(key=lambda c: c.value)

    def remove_cards(self, indices: List[int]):
        for i in sorted(indices, reverse=True):
            del self.cards[i]
        self.sort()

    def remove_card_objects(self, cards_to_remove: List[Card]):
        for target in cards_to_remove:
            self.cards.remove(target)
        self.sort()
