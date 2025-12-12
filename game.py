from cards import *
from logger import Logger
class Round:
    def __init__(self, players, dealer_index, force_dealer_pick_up=False, logger=None):
        self.players = players
        self.dealer_index = dealer_index
        self.force_dealer_pick_up = force_dealer_pick_up
        self.logger = logger or Logger()
        self.trump_suit = None
        self.declaring_team = None
        self.trump_chooser = None
        self.out_of_play = []

    def choose_trump(self, kitty):
        upcard = kitty[0]
        first_round = True

        if not self.force_dealer_pick_up:
            for _ in range(2):
                for i in range(4):
                    p = self.players[(self.dealer_index + 1 + i) % 4]
                    pick, suit = p.choose_trump(upcard, first_round)

                    if pick:
                        dealer = self.players[self.dealer_index]
                        if first_round:
                            # ROUND 1 — ordering up
                            self.trump_suit = upcard.suit
                            self.declaring_team = p.team
                            self.trump_chooser = p

                            self.logger.log_order_up(p, dealer)

                            # Dealer picks up card
                            dealer.hand.append(upcard)
                            discard = dealer.discard(self.trump_suit)
                            dealer.hand.remove(discard)

                            self.logger.log_pickup_and_discard(dealer, upcard, discard)
                        else:
                            # ROUND 2 — calling trump
                            self.trump_suit = suit
                            self.declaring_team = p.team
                            self.trump_chooser = p
                            self.logger.log_call_trump(p, suit)

                        self.logger.log_final_trump(self.trump_suit, self.trump_chooser)
                        return
                first_round = False  # move to second round
                self.out_of_play.append(upcard) # upcard is flipped over

            dealer = self.players[self.dealer_index]
            self.trump_suit = dealer.forced_choose_trump(upcard.suit)
            self.declaring_team = dealer.team
            self.trump_chooser = dealer

            self.logger.log_forced_trump(dealer, self.trump_suit)
            self.logger.log_final_trump(self.trump_suit, dealer)
        else:
            dealer = self.players[self.dealer_index]
            self.trump_suit = upcard.suit
            self.declaring_team = dealer.team
            self.trump_chooser = dealer

            self.logger.log_order_up(dealer, dealer)

            dealer.hand.append(upcard)
            discard = dealer.discard(self.trump_suit)
            dealer.hand.remove(discard)

            self.logger.log_pickup_and_discard(dealer, upcard, discard)

    def play_trick(self, leader_index):
        trick = []
        lead_suit = None
        for i in range(4):
            p = self.players[(leader_index + i) % 4]
            card = p.play_card(trick, self.out_of_play, self.trump_suit, lead_suit)
            p.hand.remove(card)
            trick.append((p, card))
            if not lead_suit:
                if card.rank == "J" and card.suit == SAME_COLOR[self.trump_suit]:
                    lead_suit = self.trump_suit
                else:
                    lead_suit = card.suit
            self.logger.log_card_played(p, card)

        winner = max(trick, key=lambda pc: pc[1].value(self.trump_suit, lead_suit))
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
