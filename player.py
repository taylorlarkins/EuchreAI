# player.py
import random

class Player:
    def __init__(self, name, team):
        self.name = name
        self.team = team
        self.hand = []

    def set_hand(self, cards):
        self.hand = cards

    def choose_trump(self, upcard, can_pick, forbidden_suit=None):
        """Return (bool, suit) — True to order up, or pick a suit in 2nd round."""
        return False, None  # Always pass by default

    def play_card(self, trick, lead_suit, trump):
        """Return the card the player plays."""
        playable = [c for c in self.hand if c.suit == lead_suit] or self.hand
        chosen = random.choice(playable)
        self.hand.remove(chosen)
        return chosen

# Example simple AI
class RandomAgent(Player):
    def choose_trump(self, upcard, can_pick, forbidden_suit=None):
        if random.random() < 0.3:
            return True, upcard.suit
        elif not can_pick and random.random() < 0.3:
            suits = [s for s in ["Hearts","Diamonds","Clubs","Spades"] if s != forbidden_suit]
            return True, random.choice(suits)
        return False, None
