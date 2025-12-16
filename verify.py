import re
import os
from collections import defaultdict

# ==============================
# Card utilities
# ==============================

RANK_ORDER = ["9", "10", "Q", "K", "A"]  # J handled separately due to bowers

def parse_card(card):
    """Return (rank, suit) for a card like 'J♣'."""
    rank = card[:-1]
    suit = card[-1]
    return rank, suit

def is_left_bower(card, trump):
    """Left bower = Jack of same-color suit as trump."""
    rank, suit = parse_card(card)
    if rank != "J":
        return False
    if trump == "♣" and suit == "♠":
        return True
    if trump == "♠" and suit == "♣":
        return True
    if trump == "♦" and suit == "♥":
        return True
    if trump == "♥" and suit == "♦":
        return True
    return False

def is_right_bower(card, trump):
    rank, suit = parse_card(card)
    return rank == "J" and suit == trump

def card_effective_suit(card, trump):
    """Return suit used for following suit logic."""
    if is_right_bower(card, trump) or is_left_bower(card, trump):
        return trump
    return parse_card(card)[1]


# ==============================
# Trick winner evaluation
# ==============================

def card_strength(card, trump, led_suit):
    """Return numeric strength of a played card."""
    rank, suit = parse_card(card)

    # Right bower
    if is_right_bower(card, trump):
        return 100

    # Left bower
    if is_left_bower(card, trump):
        return 99

    # Trump cards
    if card_effective_suit(card, trump) == trump:
        return 80 + RANK_ORDER.index(rank)

    # Led suit cards
    if card_effective_suit(card, trump) == led_suit:
        return 40 + RANK_ORDER.index(rank)

    # Everything else loses
    return 0


def compute_winner(trick, trump):
    """Given a trick [(player, card)], compute the true winner."""
    led_suit = card_effective_suit(trick[0][1], trump)
    strengths = [(card_strength(card, trump, led_suit), player)
                 for player, card in trick]
    strengths.sort(reverse=True)
    return strengths[0][1]


# ==============================
# Game Parser
# ==============================

def parse_game(filename):
    with open(filename, "r", encoding="utf8") as f:
        text = f.read()

    rounds = []
    blocks = re.split(r"--- ROUND", text)
    for blk in blocks[1:]:
        blk = blk.strip()
        round_num = int(blk.split("---")[0].strip(" #"))
        rounds.append((round_num, blk))
    return rounds


# ==============================
# Main Validator
# ==============================

def validate_game(filename):
    rounds = parse_game(filename)
    errors = []

    # -------------------------------
    # First pass: structural + ownership
    # -------------------------------
    for round_num, text in rounds:

        m = re.search(r"Trump:\s*([♣♠♥♦])", text)
        if not m:
            errors.append(f"[Round {round_num}] Missing trump declaration.")
            continue
        trump = m.group(1)

        hands = {}
        for p in ["P1", "P2", "P3", "P4"]:
            m = re.search(rf"{p} hand:\s*\[(.*?)\]", text)
            if not m:
                errors.append(f"[Round {round_num}] Missing hand for {p}.")
                continue
            hands[p] = m.group(1).split()

        pickup = re.search(r"(P[1-4]) picks up\s*\[(.*?)\]\s*and discards\s*\[(.*?)\]", text)
        if pickup:
            pl, up, dis = pickup.groups()
            hands[pl].append(up)
            if dis not in hands[pl]:
                errors.append(f"[Round {round_num}] {pl} discards card not in hand: {dis}")
            else:
                hands[pl].remove(dis)

        plays = re.findall(r"(P[1-4]) plays ([0-9JQKA]+[♣♠♥♦])", text)
        if len(plays) != 20:
            errors.append(f"[Round {round_num}] Expected 20 card plays, found {len(plays)}")

        for p, card in plays:
            if card not in hands[p]:
                errors.append(f"[Round {round_num}] {p} plays card not in hand: {card}")
            else:
                hands[p].remove(card)

    # -------------------------------
    # Second pass: follow-suit validation
    # -------------------------------
    errors.extend(validate_follow_suit(filename))

    # -------------------------------
    # Report
    # -------------------------------
    if errors:
        print("======== INVALID GAME ========")
        for e in errors:
            print(e)
    else:
        print("======== VALID GAME ========")


# ==============================
# Second-pass suit validation
# ==============================

def validate_follow_suit(filename):
    rounds = parse_game(filename)
    errs = []

    for round_num, text in rounds:

        m = re.search(r"Trump:\s*([♣♠♥♦])", text)
        if not m:
            continue
        trump = m.group(1)

        hands = {}
        for p in ["P1", "P2", "P3", "P4"]:
            hands[p] = re.search(rf"{p} hand:\s*\[(.*?)\]", text).group(1).split()

        pickup = re.search(r"(P[1-4]) picks up\s*\[(.*?)\]\s*and discards\s*\[(.*?)\]", text)
        if pickup:
            pl, up, dis = pickup.groups()
            hands[pl].append(up)
            if dis not in hands[pl]:
                errs.append(f"[Round {round_num}] {pl} discards card not in hand: {dis}")
            else:
                hands[pl].remove(dis)

        plays = re.findall(r"(P[1-4]) plays ([0-9JQKA]+[♣♠♥♦])", text)
        tricks = [plays[i:i+4] for i in range(0, len(plays), 4)]

        for t_index, trick in enumerate(tricks, start=1):
            if not trick:
                continue

            led_player, led_card = trick[0]
            led_suit = card_effective_suit(led_card, trump)

            pre_hands = {p: hands[p].copy() for p in hands}

            for p, card in trick:
                eff_suit = card_effective_suit(card, trump)

                if p != led_player:
                    must_follow = any(
                        card_effective_suit(c, trump) == led_suit
                        for c in pre_hands[p]
                    )
                    if must_follow and eff_suit != led_suit:
                        errs.append(
                            f"[Round {round_num}, Trick {t_index}] {p} fails to follow suit: "
                            f"led {led_suit}, played {card}, hand={pre_hands[p]}"
                        )

                if card not in hands[p]:
                    errs.append(f"[Round {round_num}, Trick {t_index}] {p} plays card not in hand: {card}")
                else:
                    hands[p].remove(card)

    return errs


# ==============================
# Directory / CLI support
# ==============================

def validate_path(path):
    if os.path.isfile(path):
        print(f"\n=== Checking {path} ===")
        validate_game(path)
        return

    if os.path.isdir(path):
        files = sorted(f for f in os.listdir(path) if f.lower().endswith(".txt"))
        if not files:
            print(f"No .txt files found in directory: {path}")
            return
        for fname in files:
            full_path = os.path.join(path, fname)
            print(f"\n=== Checking {full_path} ===")
            validate_game(full_path)
        return

    print(f"Error: path does not exist: {path}")


# ==============================
# Entry point
# ==============================

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python validate_euchre.py <gamefile.txt | directory>")
        sys.exit(1)

    validate_path(sys.argv[1])