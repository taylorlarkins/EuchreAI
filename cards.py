import random

SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
RANKS = ["9", "10", "J", "Q", "K", "A"]
SUIT_SYMBOLS = {
    "Hearts": "♥",
    "Diamonds": "♦",
    "Clubs": "♣",
    "Spades": "♠"
}
SAME_COLOR = {
    "Hearts": "Diamonds",
    "Diamonds": "Hearts",
    "Clubs": "Spades",
    "Spades": "Clubs",
}

UNKNOWN = 0
HAS = 1
LACKS = 2

def effective_suit(card, trump_suit):
    """
    Returns the suit a card effectively has for follow-suit purposes.
    """
    if card.rank == "J" and SAME_COLOR[card.suit] == trump_suit:
        return trump_suit
    return card.suit

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    def short(self):
        rank_part = self.rank if self.rank == "10" else self.rank[0]
        return f"{rank_part}{SUIT_SYMBOLS[self.suit]}"
    
    # Consider improving this valuation
    def value(self, trump_suit, lead_suit):
        """Returns a numerical value for comparing cards."""
        order = ["9", "10", "J", "Q", "K", "A"]
        if self.rank == "J":
            if self.suit == trump_suit:
                return 200
            elif SAME_COLOR[self.suit] == trump_suit:
                return 199
        if self.suit == trump_suit:
            return 100 + order.index(self.rank)
        elif self.suit == lead_suit:
            return 10 + order.index(self.rank)
        return order.index(self.rank)

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
    

class ChanceChart:    
    def __init__(self, nbr, hand):
        self.nbr = nbr
        self.chart = {player: {suit: {rank: UNKNOWN for rank in RANKS} for suit in SUITS} for player in range(1, 6)}
        self.probs = {player: {suit: {rank: 0.0 for rank in RANKS} for suit in SUITS} for player in range(1, 6)}
        for card in hand:
            self.confirmed_holder(self.nbr, card.suit, card.rank)
        self.remaining_cards = 24
        self.hand_sizes = {1: 5, 2: 5, 3: 5, 4: 5, 5: 4}
        self.accounted = set()

    def update(self, trick, trump_suit, lead_suit):
        self.update_chart(trick, trump_suit, lead_suit)
        self.update_probs()

    def update_chart(self, trick, trump_suit, lead_suit):
        for player, card in trick:
            p = player.nbr
            s = effective_suit(card, trump_suit)
            r = card.rank

            # Since p played c, p no longer holds c and no other players can have c
            self.card_played(p, card.suit, r)

            # If p does not follow s, p has no other cards of s
            if s != lead_suit:
                self.did_not_follow(p, lead_suit, trump_suit)

    def update_probs(self):
        for suit in SUITS:
            for rank in RANKS:
                # If card has been played or we already know who has it we can skip
                if (suit, rank) in self.accounted: continue
                maybe_here = []
                not_here = []
                for player in range(1, 6):
                    status = self.chart[player][suit][rank]
                    if status == HAS:
                        self.confirmed_holder(player, suit, rank)
                    elif status == UNKNOWN:
                        maybe_here.append(player)
                    else:
                        not_here.append(player)
                if len(maybe_here) == 1:
                    self.confirmed_holder(player, suit, rank)
                elif maybe_here:
                    for player in maybe_here:
                        self.probs[player][suit][rank] = (self.hand_sizes[player] / self.remaining_cards)
                    
    def get_others(self, player_nbr):
        return [p for p in range(1, 6) if p != player_nbr]
    
    def confirmed_holder(self, player_nbr, suit, rank):
        self.chart[player_nbr][suit][rank] = HAS
        self.probs[player_nbr][suit][rank] = 1.0
        others = self.get_others(player_nbr)
        for o in others:
            self.chart[o][suit][rank] = LACKS
            self.probs[o][suit][rank] = 0.0
        self.accounted.add((suit, rank))
    
    def card_played(self, player_nbr, suit, rank):
        self.remaining_cards -= 1
        self.hand_sizes[player_nbr] -= 1
        self.chart[player_nbr][suit][rank] = LACKS
        self.probs[player_nbr][suit][rank] = 0.0
        others = self.get_others(player_nbr)
        for o in others:
            self.chart[o][suit][rank] = LACKS
            self.probs[o][suit][rank] = 0.0
        self.accounted.add((suit, rank))
    
    def did_not_follow(self, player_nbr, lead_suit, trump_suit):
        for rank in RANKS:
            self.chart[player_nbr][lead_suit][rank] = LACKS
            self.probs[player_nbr][lead_suit][rank] = 0.0
        if lead_suit == trump_suit:
            self.chart[player_nbr][SAME_COLOR[lead_suit]]["J"] = LACKS
            self.probs[player_nbr][SAME_COLOR[lead_suit]]["J"] = 0.0

    def pretty_print(self):
        for player in sorted(self.probs.keys()):
            print(f"\nPlayer {player}") if player != 5 else print(f"\nKitty")
            print("-" * 60)
            header = "Suit".ljust(12) + "".join(rank.rjust(8) for rank in RANKS)
            print(header)
            print("-" * len(header))

            for suit in SUITS:
                row = suit.ljust(12)
                for rank in RANKS:
                    value = self.probs[player][suit][rank]
                    row += f"{value:.3f}".rjust(8)
                print(row)