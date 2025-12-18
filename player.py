import random
import itertools
from cards import *
class Player:
    def __init__(self, number: int, teammate: int, team: int):
        self.nbr = number
        self.teammate = teammate
        self.team = team
        self.hand = []
        self.declaring_team = None
        self.tricks_won = 0

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

    # Agents may use this function to perform actions after receiving their hand
    def reset(self):
        pass

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
    
class MonteCarlo(Player):
    def __init__(self, number, teammate, team):
        super().__init__(number, teammate, team)

    def reset(self):
        self.other_cards = set(itertools.product(SUITS, RANKS))
        for card in self.hand:
            self.other_cards.discard((card.suit, card.rank))
    
    def choose_trump(self, upcard, first_round):
        # TODO: Make this a Monte Carlo process
        return choose_ge3(self, upcard, first_round)
    
    def forced_choose_trump(self, forbidden):
        # TODO: Make this a Monte Carlo process
        return forced_choose_max_suit_count(self, forbidden)
    
    def discard(self, trump):
        # TODO: Maybe make this a Monte Carlo process?
        return discard_lowest_nontrump_rank(self, trump)
    
    def play_card(self, trick, trump_suit, lead_suit):
        card_count = len(self.hand)
        cards_per_player = {p: card_count for p in range(1, 5)}
        for player, card in trick:
            self.other_cards.discard((card.suit, card.rank))
            cards_per_player[player.nbr] -= 1
        playable = get_playable_cards(self, trump_suit, lead_suit)
        if len(playable) == 1:
            return playable[0]
        mc_results = []
        trick_wins = {self.team: self.tricks_won, 1 - self.team: 5 - len(self.hand) - self.tricks_won}
        for card in playable:
            mc_results.append(self.monte_carlo(trick, trump_suit, lead_suit, cards_per_player, card, trick_wins))
        max_index = mc_results.index(max(mc_results))
        return playable[max_index]

    def monte_carlo(self, trick, trump_suit, lead_suit, cards_per_player, card_to_play, trick_wins):
        partial_deck = [Card(pair[0], pair[1]) for pair in self.other_cards]
        players = {1: HighWithCaution(1, 3, 0), 2: HighWithCaution(2, 4, 1), 3: HighWithCaution(3, 1, 0), 4: HighWithCaution(4, 2, 0)}
        score_sum = 0
        for _ in range(1000):
            sim_trick = trick.copy()
            sim_lead_suit = lead_suit
            sim_trick_wins = trick_wins.copy()
            # Assign players their cards
            players[self.nbr].set_hand(self.hand.copy())
            pdc = partial_deck.copy()
            random.shuffle(pdc)
            for p in range(1, 5):
                if p == self.nbr: continue
                card_count = cards_per_player[p]
                players[p].set_hand(pdc[-card_count:].copy())
                del pdc[-card_count:]
            
            # Finish the current trick
            for card in players[self.nbr].hand:
                if card.suit == card_to_play.suit and card.rank == card_to_play.rank:
                    sim_trick.append((players[self.nbr], card))
                    players[self.nbr].hand.remove(card)
                    break
            if sim_lead_suit == None:
                sim_lead_suit = effective_suit(card_to_play, trump_suit)
            left = 4 - len(sim_trick)
            prev_index = self.nbr
            for _ in range(left):
                p = players[(prev_index % 4) + 1]
                card = p.play_card(sim_trick, trump_suit, sim_lead_suit)
                p.hand.remove(card)
                sim_trick.append((p, card))
                prev_index = p.nbr
            winner = max(sim_trick, key=lambda pc: pc[1].value(trump_suit, sim_lead_suit))
            sim_trick_wins[winner[0].team] += 1
            next_index = winner[0].nbr

            # Play remaining tricks
            tricks_remaining = len(players[1].hand)
            for _ in range(tricks_remaining):
                sim_trick = []
                sim_lead_suit = None
                for _ in range(4):
                    p = players[next_index]
                    card = p.play_card(sim_trick, trump_suit, sim_lead_suit)
                    p.hand.remove(card)
                    sim_trick.append((p, card))
                    if sim_lead_suit is None:
                        sim_lead_suit = effective_suit(card, trump_suit)
                    next_index = (next_index % 4) + 1
                winner = max(sim_trick, key=lambda pc: pc[1].value(trump_suit, sim_lead_suit))
                sim_trick_wins[winner[0].team] += 1
                next_index = winner[0].nbr
            
            # Determine outcome
            dec_team = self.declaring_team
            opp_team = 1 - dec_team
            dec_tricks = sim_trick_wins[dec_team]
            scores = {0: 0, 1: 0}
            if dec_tricks >= 3:
                scores[dec_team] += 1 if dec_tricks < 5 else 2
            else:
                scores[opp_team] += 2

            score_sum += scores[self.team]
        return score_sum / 1000