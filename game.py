from cards import *
from logger import Logger

def card_value(card, trump, lead_suit):
    """Returns a numerical value for comparing cards."""
    order = ["9", "10", "J", "Q", "K", "A"]

    # Identify left and right bowers
    same_color = {
        "Hearts": "Diamonds",
        "Diamonds": "Hearts",
        "Clubs": "Spades",
        "Spades": "Clubs",
    }

    if card.rank == "J":
        if card.suit == trump:
            return 200  # Right Bower
        elif same_color[card.suit] == trump:
            return 199  # Left Bower

    if card.suit == trump:
        return 100 + order.index(card.rank)

    elif card.suit == lead_suit:
        return 10 + order.index(card.rank)

    return 0

class Round:
    def __init__(self, players, dealer_index, logger=None):
        self.players = players
        self.dealer_index = dealer_index
        self.logger = logger or Logger()
        self.trump = None
        self.declaring_team = None
        self.trump_chooser = None
        self.out_of_play = []

    def choose_trump(self, kitty):
        upcard = kitty[0]
        first_round = True
        forbidden_suit = upcard.suit

        for _ in range(2):
            for i in range(4):
                p = self.players[(self.dealer_index + 1 + i) % 4]
                pick, suit = p.choose_trump(upcard, first_round, forbidden_suit)

                if pick:
                    dealer = self.players[self.dealer_index]

                    if first_round:
                        # ROUND 1 — ordering up
                        self.trump = upcard.suit
                        self.declaring_team = p.team
                        self.trump_chooser = p

                        self.logger.log_order_up(p, dealer)

                        # Dealer picks up card
                        dealer.hand.append(upcard)
                        discard = dealer.discard(self.out_of_play, self.trump)
                        dealer.hand.remove(discard)

                        self.logger.log_pickup_and_discard(dealer, upcard, discard)

                    else:
                        # ROUND 2 — calling trump
                        self.trump = suit
                        self.declaring_team = p.team
                        self.trump_chooser = p
                        self.logger.log_call_trump(p, suit)

                    self.logger.log_final_trump(self.trump, self.trump_chooser)
                    return

            first_round = False  # move to second round
            self.out_of_play.append(upcard) # upcard is flipped over

        dealer = self.players[self.dealer_index]
        suits = [s for s in SUITS if s != forbidden_suit]
        self.trump = dealer.forced_choose_trump(suits)
        self.declaring_team = dealer.team
        self.trump_chooser = dealer

        self.logger.log_forced_trump(dealer, self.trump)
        self.logger.log_final_trump(self.trump, dealer)

    def play_trick(self, leader_index):
        trick = []
        lead_card = None
        for i in range(4):
            p = self.players[(leader_index + i) % 4]
            card = p.play_card(trick, self.out_of_play, lead_card.suit if lead_card else None, self.trump)
            p.hand.remove(card)
            trick.append((p, card))
            if not lead_card:
                lead_card = card
            self.logger.log_card_played(p, card)

        winner = max(trick, key=lambda pc: card_value(pc[1], self.trump, lead_card.suit))
        self.out_of_play += [pair[1] for pair in trick]
        self.logger.log_trick_winner(winner[0], winner[1])
        return self.players.index(winner[0])

    def play_round(self):
        tricks_won = {p.team: 0 for p in self.players}
        leader = (self.dealer_index + 1) % 4
        for _ in range(5):
            leader = self.play_trick(leader)
            tricks_won[self.players[leader].team] += 1
        return tricks_won
