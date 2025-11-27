from datetime import datetime
from cards import SUIT_SYMBOLS
import os

class Logger:
    def __init__(self, filename=None, directory=None):
        self.filename = filename or f"euchre_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.directory = directory
        self.lines = []
        self.round_number = 0

    def start_round(self, round_num, dealer, hands, upcard):
        self.round_number = round_num
        self.lines.append(f"\n--- ROUND #{round_num} ---")
        self.lines.append(f"Dealer: P{dealer.nbr}")
        self.lines.append(f"Upcard: {upcard.short()}")
        for p in hands:
            hand_str = " ".join([c.short() for c in p.hand])
            self.lines.append(f"P{p.nbr} hand: [{hand_str}]")
        self.lines.append("")  # blank line before bidding

    def log_order_up(self, chooser, dealer):
        self.lines.append(f"P{chooser.nbr} orders up P{dealer.nbr}")

    def log_pickup_and_discard(self, dealer, upcard, discard):
        self.lines.append(f"P{dealer.nbr} picks up [{upcard.short()}] and discards [{discard.short()}]")

    def log_call_trump(self, chooser, suit):
        symbol = SUIT_SYMBOLS[suit]
        self.lines.append(f"P{chooser.nbr} calls {symbol} as trump")

    def log_forced_trump(self, dealer, suit):
        symbol = SUIT_SYMBOLS[suit]
        self.lines.append(f"Dealer P{dealer.nbr} chooses {symbol} as trump")

    def log_final_trump(self, suit, chooser):
        symbol = SUIT_SYMBOLS[suit]
        self.lines.append(f"Trump: {symbol} (chosen by P{chooser.nbr})\n")

    def log_card_played(self, player, card):
        self.lines.append(f"  P{player.nbr} plays {card.short()}")

    def log_trick_winner(self, player, card):
        self.lines.append(f"  Winner: P{player.nbr} ({card.short()})")

    def log_round_end(self, tricks, declaring_team, scores):
        self.lines.append("\nRound result:")
        for team, tcount in tricks.items():
            self.lines.append(f"  Team {team}:         {tcount} tricks")
        self.lines.append(f"  Called By:      Team {declaring_team}")
        self.lines.append(f"  Scores:         Team 0: {scores[0]}, Team 1: {scores[1]}")

    def save(self):
        if self.directory is None:
            filepath = self.filename
        else:
            os.makedirs(self.directory, exist_ok=True)
            filepath = os.path.join(self.directory, self.filename)

        with open(filepath, "w") as f:
            f.write("\n".join(self.lines))
