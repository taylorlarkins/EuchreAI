# player.py
import random
from cards import SUITS
from game import card_value

class Player:
    def __init__(self, name, team):
        self.name = name
        self.team = team
        self.hand = []

    def set_hand(self, cards):
        self.hand = cards
    
    def get_suit_counts(self):
        suit_counts = {s: 0 for s in SUITS}
        for card in self.hand:
            suit_counts[card.suit] += 1
        return suit_counts

    # Override the following methods to create an agent
    def choose_trump(self, upcard, first_round):
        if first_round:
            return (True, upcard.suit) if random.random() < 0.5 else (False, None)
        return (True, random.choice([s for s in SUITS if s != upcard.suit])) if random.random() < 0.5 else (False, None)

    def play_card(self, trick, out_of_play, lead_suit, trump_suit):
        playable = [c for c in self.hand if c.suit == lead_suit] or self.hand
        return random.choice(playable)
    
    def forced_choose_trump(self, forbidden):
        options = SUITS[:]
        options.remove(forbidden)
        return random.choice(options)
    
    def discard(self, trump):
        return random.choice(self.hand)

class Random(Player):
    # uses default play_card function

    def choose_trump(self, upcard, first_round):
            suit_counts = self.get_suit_counts()
            if first_round:
                if suit_counts[upcard.suit] >= 3:
                    return (True, upcard.suit)
                return (False, None)
            del suit_counts[upcard.suit]
            for suit in suit_counts.keys():
                if suit_counts[suit] >= 3:
                    return (True, suit)
            return (False, None)
    
    def forced_choose_trump(self, forbidden):
        suit_counts = self.get_suit_counts()
        del suit_counts[forbidden]
        return max(suit_counts, key=suit_counts.get)
    
    def discard(self, trump):
        sorted_hand = sorted(self.hand, key=lambda x: x.rank)
        for card in sorted_hand:
            if card.suit != trump:
                return card
        return sorted_hand[0]
    
class HighCard(Player):
    def choose_trump(self, upcard, first_round):
        suit_counts = self.get_suit_counts()
        if first_round:
            if suit_counts[upcard.suit] >= 3:
                return (True, upcard.suit)
            return (False, None)
        del suit_counts[upcard.suit]
        for suit in suit_counts.keys():
            if suit_counts[suit] >= 3:
                return (True, suit)
        return (False, None)
        
    def play_card(self, trick, out_of_play, lead_suit, trump_suit):
        playable = [c for c in self.hand if c.suit == lead_suit] or self.hand
        playable.sort(key=lambda x: card_value(x, trump_suit, lead_suit), reverse=True)
        return playable[0]
    
    def forced_choose_trump(self, forbidden):
        suit_counts = self.get_suit_counts()
        del suit_counts[forbidden]
        return max(suit_counts, key=suit_counts.get)
    
    def discard(self, trump):
        sorted_hand = sorted(self.hand, key=lambda x: x.rank)
        for card in sorted_hand:
            if card.suit != trump:
                return card
        return sorted_hand[0]
    
class LowCard(Player):
    def choose_trump(self, upcard, first_round):
        suit_counts = self.get_suit_counts()
        if first_round:
            if suit_counts[upcard.suit] >= 3:
                return (True, upcard.suit)
            return (False, None)
        del suit_counts[upcard.suit]
        for suit in suit_counts.keys():
            if suit_counts[suit] >= 3:
                return (True, suit)
        return (False, None)
        
    def play_card(self, trick, out_of_play, lead_suit, trump_suit):
        playable = [c for c in self.hand if c.suit == lead_suit] or self.hand
        playable.sort(key=lambda x: card_value(x, trump_suit, lead_suit), reverse=False)
        return playable[0]
    
    def forced_choose_trump(self, forbidden):
        suit_counts = self.get_suit_counts()
        del suit_counts[forbidden]
        return max(suit_counts, key=suit_counts.get)
    
    def discard(self, trump):
        sorted_hand = sorted(self.hand, key=lambda x: x.rank)
        for card in sorted_hand:
            if card.suit != trump:
                return card
        return sorted_hand[0]