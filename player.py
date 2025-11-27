import random
from cards import SUITS, Card
from game import card_value

class Player:
    def __init__(self, number: int, teammate: int, team: int):
        self.nbr = number
        self.teammate = teammate
        self.team = team
        self.hand = []

    def set_hand(self, cards):
        self.hand = cards
    
    def get_suit_counts(self):
        """
        Return a dictionary with the counts of each suit in a player's hand.
        """
        suit_counts = {s: 0 for s in SUITS}
        for card in self.hand:
            suit_counts[card.suit] += 1
        return suit_counts
    
    def get_teammates_play(self, trick):
        """
        Returns the card played by the player's teammate, or None if they have
        not played yet this trick.
        """
        for p, card in trick:
            if p == self.teammate:
                return card
        return None

    # Override the following methods to create an agent
    def choose_trump(self, upcard: Card, first_round: bool):
        if first_round:
            return (True, upcard.suit) if random.random() < 0.5 else (False, None)
        return (True, random.choice([s for s in SUITS if s != upcard.suit])) if random.random() < 0.5 else (False, None)

    def forced_choose_trump(self, forbidden: str):
        options = SUITS[:]
        options.remove(forbidden)
        return random.choice(options)
    
    def discard(self, trump: str):
        return random.choice(self.hand)
    
    def play_card(self, trick: list[tuple[int, Card]], out_of_play: list[Card], lead_suit: str, trump_suit: str):
        playable = [c for c in self.hand if c.suit == lead_suit] or self.hand
        return random.choice(playable)
    
##### ----- CHOOSE TRUMP FUNCTIONS ----- #####
def choose_ge3(self: Player, upcard: Card, first_round: bool):
    """
    Round 1: Order up dealer if player has 3 or more cards of the upcard suit. \\
    Round 2: If player has 3 or more cards of a suit, pick that suit, otherwise pass.
    """
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

##### ----- FORCED CHOOSE TRUMP FUNCTIONS ----- #####
def forced_choose_max_suit_count(self, forbidden: str):
    """
    Pick the allowed suit that the player has the most of.
    """
    suit_counts = self.get_suit_counts()
    del suit_counts[forbidden]
    return max(suit_counts, key=suit_counts.get)

##### ----- PLAY CARD FUNCTIONS ----- #####
def play_highest_value(self, lead_suit: str, trump_suit: str):
    """
    Play the card with the highest value.
    """
    playable = [c for c in self.hand if c.suit == lead_suit] or self.hand
    playable.sort(key=lambda x: card_value(x, trump_suit, lead_suit), reverse=True)
    return playable[0]

def play_lowest_value(self, lead_suit: str, trump_suit: str):
    """
    Play the card with the lowest value.
    """
    playable = [c for c in self.hand if c.suit == lead_suit] or self.hand
    playable.sort(key=lambda x: card_value(x, trump_suit, lead_suit), reverse=False)
    return playable[0]

##### ----- DISCARD FUNCTIONS ----- #####
def discard_lowest_nontrump_rank(self: Player, trump: str):
    """
    Discard the lowest rank card that is not of the trump suit. If all cards are of
    the trump suit, discard the lowest rank card.
    """
    sorted_hand = sorted(self.hand, key=lambda x: x.rank)
    for card in sorted_hand:
        if card.suit != trump:
            return card
    return sorted_hand[0]

##### ----- PLAYERS ----- #####
class SmartRandom(Player):
    def choose_trump(self, upcard, first_round):
        return choose_ge3(self, upcard, first_round)
    
    def forced_choose_trump(self, forbidden):
        return forced_choose_max_suit_count(self, forbidden)
    
    def discard(self, trump):
        return discard_lowest_nontrump_rank(self, trump)
    
    def play_card(self, trick, out_of_play, lead_suit, trump_suit):
        return super().play_card(trick, out_of_play, lead_suit, trump_suit)

class HighValue(Player):
    def choose_trump(self, upcard, first_round):
        return choose_ge3(self, upcard, first_round)
    
    def forced_choose_trump(self, forbidden):
        return forced_choose_max_suit_count(self, forbidden)
    
    def discard(self, trump):
        return discard_lowest_nontrump_rank(self, trump)
    
    def play_card(self, trick, out_of_play, lead_suit, trump_suit):
        return play_highest_value(self, lead_suit, trump_suit)
    
class LowValue(Player):
    def choose_trump(self, upcard, first_round):
        return choose_ge3(self, upcard, first_round)
    
    def forced_choose_trump(self, forbidden):
        return forced_choose_max_suit_count(self, forbidden)
    
    def discard(self, trump):
        return discard_lowest_nontrump_rank(self, trump)
    
    def play_card(self, trick, out_of_play, lead_suit, trump_suit):
        return play_lowest_value(self, lead_suit, trump_suit)

#TODO: implement play_card
class HighWithCaution(Player):
    def choose_trump(self, upcard, first_round):
        return choose_ge3(self, upcard, first_round)
    
    def forced_choose_trump(self, forbidden):
        return forced_choose_max_suit_count(self, forbidden)
    
    def discard(self, trump):
        return discard_lowest_nontrump_rank(self, trump)
    
    def play_card(self, trick, out_of_play, lead_suit, trump_suit):
        pass