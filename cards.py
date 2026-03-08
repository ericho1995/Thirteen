"""Thirteen Game - Cards Module"""
from typing import List
from dataclasses import dataclass
from enum import Enum

@dataclass
class Card:
    rank: str
    suit: str
    value: int  # 3=3 to 2=15

    def __str__(self):
        return f"{self.rank}{self.suit}"

RANKS = ['3','4','5','6','7','8','9','T','J','Q','K','A','2']  # T=10
SUITS = ['♠','♥','♦','♣']
VALUES = {r: i+3 for i, r in enumerate(RANKS)}

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
        import random
        random.shuffle(self.cards)
    
    def deal(self, num: int) -> List[Card]:
        return [self.cards.pop() for _ in range(num)]

class Hand:
    def __init__(self, cards: List[Card]):
        self.cards = sorted(cards, key=lambda c: c.value)
    
    def __len__(self):
        return len(self.cards)
    
    def is_empty(self):
        return len(self.cards) == 0
    
    def remove_cards(self, indices: List[int]):
        indices.sort(reverse=True)
        for i in indices:
            del self.cards[i]
        self.cards.sort(key=lambda c: c.value)
