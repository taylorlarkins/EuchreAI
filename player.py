import random
from cards import *
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
    
    def play_card(self, trick: list[tuple[int, Card]], trump_suit: str, lead_suit: str):
        playable = get_playable_cards(self, trump_suit, lead_suit)
        return random.choice(playable)

##### ----- HELPERS ----- #####
def get_current_winner(trick, trump_suit, lead_suit):
    """
    Returns the player and card that is currently winning the trick. Returns (None, None)
    if no one has played card yet.
    """
    winner = None
    winner_card = None
    winner_card_value = -1
    for p, card in trick:
        c_value = card.value(trump_suit, lead_suit)
        if c_value > winner_card_value:
            winner = p
            winner_card = card
            winner_card_value = c_value
    return winner, winner_card

def get_playable_cards(self: Player, trump_suit: str, lead_suit: str | None):
    """
    Returns a list of cards the player is legally allowed to play.
    """
    if lead_suit is None:
        return list(self.hand)
    playable = [
        c for c in self.hand
        if effective_suit(c, trump_suit) == lead_suit
    ]
    return playable if playable else list(self.hand)

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
def play_highest_value(self, trump_suit: str, lead_suit: str):
    """
    Play the card with the highest value.
    """
    playable = get_playable_cards(self, trump_suit, lead_suit)
    playable.sort(key=lambda x: x.value(trump_suit, lead_suit), reverse=True)
    return playable[0]

def play_lowest_value(self, trump_suit: str, lead_suit: str):
    """
    Play the card with the lowest value.
    """
    playable = get_playable_cards(self, trump_suit, lead_suit)
    playable.sort(key=lambda x: x.value(trump_suit, lead_suit), reverse=False)
    return playable[0]

def play_lowest_winner(self, trump_suit: str, lead_suit: str, current_winner: Card):
    """
    Play the lowest value card that will beat the current winning card. If no cards
    can win then play the lowest valued card.
    """
    playable = get_playable_cards(self, trump_suit, lead_suit)
    playable.sort(key=lambda x: x.value(trump_suit, lead_suit), reverse=False)
    winner_value = current_winner.value(trump_suit, lead_suit)
    for c in playable:
        if c.value(trump_suit, lead_suit) > winner_value:
            return c
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
    
    def play_card(self, trick, trump_suit, lead_suit):
        return super().play_card(trick, trump_suit, lead_suit)

class HighValue(Player):
    def choose_trump(self, upcard, first_round):
        return choose_ge3(self, upcard, first_round)
    
    def forced_choose_trump(self, forbidden):
        return forced_choose_max_suit_count(self, forbidden)
    
    def discard(self, trump):
        return discard_lowest_nontrump_rank(self, trump)
    
    def play_card(self, trick, trump_suit, lead_suit):
        return play_highest_value(self, trump_suit, lead_suit)
    
class LowValue(Player):
    def choose_trump(self, upcard, first_round):
        return choose_ge3(self, upcard, first_round)
    
    def forced_choose_trump(self, forbidden):
        return forced_choose_max_suit_count(self, forbidden)
    
    def discard(self, trump):
        return discard_lowest_nontrump_rank(self, trump)
    
    def play_card(self, trick, trump_suit, lead_suit):
        return play_lowest_value(self, trump_suit, lead_suit)

class HighWithCaution(Player):
    def choose_trump(self, upcard, first_round):
        return choose_ge3(self, upcard, first_round)
    
    def forced_choose_trump(self, forbidden):
        return forced_choose_max_suit_count(self, forbidden)
    
    def discard(self, trump):
        return discard_lowest_nontrump_rank(self, trump)
    
    def play_card(self, trick, trump_suit, lead_suit):
        current_winner, current_winning_card = get_current_winner(trick, trump_suit, lead_suit)
        if current_winner != None and current_winner != self.teammate:
            return play_lowest_winner(self, trump_suit, lead_suit, current_winning_card)
        return play_lowest_value(self, trump_suit, lead_suit)

class TeamPlayer(Player):
    def __init__(self, number, teammate, team):
        super().__init__(number, teammate, team)
        self.chance_chart = ChanceChart(self.nbr, [])

    def choose_trump(self, upcard, first_round):
        return choose_ge3(self, upcard, first_round)
    
    def forced_choose_trump(self, forbidden):
        return forced_choose_max_suit_count(self, forbidden)
    
    def discard(self, trump):
        return discard_lowest_nontrump_rank(self, trump)
    
    def play_card(self, trick, trump_suit, lead_suit):
        return play_highest_value(self, trump_suit, lead_suit)