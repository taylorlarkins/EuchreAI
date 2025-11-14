from cards import Deck
from game import Round

class GameEngine:
    def __init__(self, players, logger=None):
        self.players = players
        self.scores = {0: 0, 1: 0}
        self.dealer_index = 0
        self.logger = logger
        self.round_counter = 1

    def play_game(self):
        while max(self.scores.values()) < 10:
            self.play_round()
            self.dealer_index = (self.dealer_index + 1) % 4
            self.round_counter += 1

    def play_round(self):
        deck = Deck()
        hands, kitty = deck.deal()
        for i, p in enumerate(self.players):
            p.set_hand(hands[i])

        rnd = Round(self.players, self.dealer_index, logger=self.logger)

        self.logger.start_round(
            self.round_counter,
            self.players[self.dealer_index],
            self.players,
            kitty[0]
        )

        rnd.choose_trump(kitty)

        tricks = rnd.play_round()
        dec_team = rnd.declaring_team
        opp_team = 1 - dec_team
        dec_tricks = tricks[dec_team]

        if dec_tricks >= 3:
            self.scores[dec_team] += 1 if dec_tricks < 5 else 2
        else:
            self.scores[opp_team] += 2

        self.logger.log_round_end(tricks, dec_team, self.scores)
