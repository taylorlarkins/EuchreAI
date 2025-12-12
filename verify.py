import re
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

    for round_num, text in rounds:
        # -------------------------------
        # Extract trump
        # -------------------------------
        m = re.search(r"Trump:\s*([♣♠♥♦])", text)
        if not m:
            errors.append(f"[Round {round_num}] Missing trump declaration.")
            continue
        trump = m.group(1)

        # -------------------------------
        # Extract initial hands
        # -------------------------------
        hands = {}
        for p in ["P1", "P2", "P3", "P4"]:
            m = re.search(rf"{p} hand:\s*\[(.*?)\]", text)
            if not m:
                errors.append(f"[Round {round_num}] Missing hand for {p}.")
                continue
            cards = m.group(1).split()
            hands[p] = cards

        # -------------------------------
        # Apply dealer pickup/discard if present
        # -------------------------------
        pickup = re.search(r"picks up\s*\[(.*?)\]\s*and discards\s*\[(.*?)\]", text)
        if pickup:
            card_up, card_dis = pickup.groups()
            # Determine who picked up (search above)
            picked_by = re.search(r"(P[1-4]) picks up", text).group(1)
            hands[picked_by].append(card_up)
            try:
                hands[picked_by].remove(card_dis)
            except ValueError:
                errors.append(f"[Round {round_num}] {picked_by} tried to discard {card_dis} which they do not have.")

        # -------------------------------
        # Parse tricks
        # -------------------------------
        trick_pattern = r"P([1-4]) plays ([0-9JQKA]+[♣♠♥♦])"
        plays = re.findall(trick_pattern, text)

        if len(plays) != 20:
            errors.append(f"[Round {round_num}] Expected 20 card plays, found {len(plays)}")

        # Group into 5 tricks of 4 plays
        tricks = [plays[i:i+4] for i in range(0, len(plays), 4)]

        # -------------------------------
        # Validate tricks
        # -------------------------------
        for t_index, trick in enumerate(tricks, start=1):

            # Check players played cards they actually had
            for p, card in trick:
                if card not in hands[f"P{p}"]:
                    errors.append(f"[Round {round_num}, Trick {t_index}] "
                                  f"P{p} played {card} but does not have it.")
                else:
                    hands[f"P{p}"].remove(card)

            # Follow-suit checking
            if trick:
                first_player, first_card = trick[0]
                led_suit = card_effective_suit(first_card, trump)

                for p, card in trick[1:]:
                    p_hand_before = hands[f"P{p}"]  # remaining cards after removing played one?
                    # Actually need hand BEFORE removal—so this requires snapshot.
                    # Workaround: re-check using copy earlier.

                # Let's re-parse trick without removing cards:
                # (We do that by re-extracting hands fresh for follow-suit logic)
                # But simpler: store original-hand copies first.

        # To simplify correct follow-suit checking,
        # we re-parse round once *with* card-removal tracking.

    # -------------------------------
    # Second pass: full correct tracking for follow-suit validation
    # -------------------------------

    errors.extend(validate_follow_suit(filename))

    # -------------------------------
    # Final result
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
    """Clean implementation: replay each round with a fresh hand snapshot."""
    rounds = parse_game(filename)
    errs = []

    for round_num, text in rounds:

        # Extract trump
        m = re.search(r"Trump:\s*([♣♠♥♦])", text)
        if not m:
            continue
        trump = m.group(1)

        # Initial hands
        hands = {}
        for p in ["P1", "P2", "P3", "P4"]:
            cards = re.search(rf"{p} hand:\s*\[(.*?)\]", text).group(1).split()
            hands[p] = cards.copy()

        # Pickup/discard
        pickup = re.search(r"(P[1-4]) picks up\s*\[(.*?)\]\s*and discards\s*\[(.*?)\]", text)
        if pickup:
            pl, up, dis = pickup.groups()
            hands[pl].append(up)
            if dis not in hands[pl]:
                errs.append(f"[Round {round_num}] {pl} discards card not in hand: {dis}")
            else:
                hands[pl].remove(dis)

        # Parse plays
        pattern = r"(P[1-4]) plays ([0-9JQKA]+[♣♠♥♦])"
        plays = re.findall(pattern, text)
        tricks = [plays[i:i+4] for i in range(0, len(plays), 4)]

        for t_index, trick in enumerate(tricks, start=1):
            if not trick:
                continue

            led_player, led_card = trick[0]
            led_suit = card_effective_suit(led_card, trump)

            # Temporarily snapshot hands for follow-suit
            pre_hands = {p: hands[p].copy() for p in hands}

            for p, card in trick:
                # Follow suit check
                eff_suit = card_effective_suit(card, trump)

                if p != led_player:
                    # Must follow if any card in hand has effective suit == led_suit
                    must_follow = any(card_effective_suit(c, trump) == led_suit
                                      for c in pre_hands[p])

                    if must_follow and eff_suit != led_suit:
                        errs.append(
                            f"[Round {round_num}, Trick {t_index}] {p} fails to follow suit: "
                            f"led {led_suit}, played {card}, hand={pre_hands[p]}"
                        )

                # Remove played card
                if card not in hands[p]:
                    errs.append(f"[Round {round_num}, Trick {t_index}] {p} plays card not in hand: {card}")
                else:
                    hands[p].remove(card)

    return errs


# ==============================
# Command-line entry point
# ==============================

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python validate_euchre.py gamefile.txt")
        sys.exit(1)

    validate_game(sys.argv[1])
