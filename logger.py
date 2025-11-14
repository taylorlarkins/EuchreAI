from datetime import datetime
from cards import SUIT_SYMBOLS

class Logger:
    def __init__(self, filename=None):
        self.filename = filename or f"euchre_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.lines = []
        self.round_number = 0

    def start_round(self, round_num, dealer, hands, upcard):
        self.round_number = round_num
        self.lines.append(f"\n--- ROUND #{round_num} ---")
        self.lines.append(f"Dealer: {dealer.name}")
        self.lines.append(f"Upcard: {upcard.short()}")
        for p in hands:
            hand_str = " ".join([c.short() for c in p.hand])
            self.lines.append(f"{p.name} hand: [{hand_str}]")
        self.lines.append("")  # blank line before bidding

    # --- NEW LOGGING METHODS ---

    def log_order_up(self, chooser, dealer):
        self.lines.append(f"{chooser.name} orders up {dealer.name}")

    def log_pickup_and_discard(self, dealer, upcard, discard):
        self.lines.append(f"{dealer.name} picks up [{upcard.short()}] and discards [{discard.short()}]")

    def log_call_trump(self, chooser, suit):
        symbol = SUIT_SYMBOLS[suit]
        self.lines.append(f"{chooser.name} calls {symbol} as trump")

    def log_forced_trump(self, dealer, suit):
        symbol = SUIT_SYMBOLS[suit]
        self.lines.append(f"Dealer {dealer.name} chooses {symbol} as trump")

    def log_final_trump(self, suit, chooser):
        symbol = SUIT_SYMBOLS[suit]
        self.lines.append(f"Trump: {symbol} (chosen by {chooser.name})\n")

    # --- Existing trick logging below ---

    def log_card_played(self, player, card):
        self.lines.append(f"  {player.name} plays {card.short()}")

    def log_trick_winner(self, player, card):
        self.lines.append(f"  Winner: {player.name} ({card.short()})")

    def log_round_end(self, tricks, declaring_team, scores):
        self.lines.append("\nRound result:")
        for team, tcount in tricks.items():
            self.lines.append(f"  Team {team}:         {tcount} tricks")
        self.lines.append(f"  Called By:      Team {declaring_team}")
        self.lines.append(f"  Scores:         Team 0: {scores[0]}, Team 1: {scores[1]}")

    def save(self):
        with open(self.filename, "w") as f:
            f.write("\n".join(self.lines))
        print(f"Log saved to {self.filename}")
