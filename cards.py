# cards.py
import random

SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
RANKS = ["9", "10", "J", "Q", "K", "A"]
SUIT_SYMBOLS = {
    "Hearts": "♥",
    "Diamonds": "♦",
    "Clubs": "♣",
    "Spades": "♠"
}

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    def short(self):
        rank_part = self.rank if self.rank == "10" else self.rank[0]
        return f"{rank_part}{SUIT_SYMBOLS[self.suit]}"

class Deck:
    def __init__(self):
        self.cards = [Card(s, r) for s in SUITS for r in RANKS]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_players=4, hand_size=5):
        self.shuffle()
        hands = [self.cards[i*hand_size:(i+1)*hand_size] for i in range(num_players)]
        kitty = self.cards[num_players*hand_size:]
        return hands, kitty
