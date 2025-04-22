import random

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

def generate_deck():
    return [rank + suit for suit in SUITS for rank in RANKS]

def deal_cards(num_players):
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [f"{r}{s}" for s in suits for r in ranks]

    random.shuffle(deck)  # full shuffle

    hands = []
    for _ in range(num_players):
        hand = random.sample(deck, 3)
        # remove dealt cards from deck
        for card in hand:
            deck.remove(card)
        hands.append(hand)

    return hands


def evaluate_hand(hand):
    """
    Returns a tuple (category_rank, [v1, v2, v3]) where:
      category_rank: 1=Trail,2=Pure Seq,3=Seq,4=Flush,5=Pair,6=High Card
      [v1,v2,v3]: sorted numeric values for tiebreakers (desc).
    """
    # map each card to its numeric value
    rank_order = {r: i for i, r in enumerate(RANKS)}
    values = sorted([rank_order[c[:-1]] for c in hand], reverse=True)
    suits  = [c[-1] for c in hand]
    ranks  = [c[:-1] for c in hand]

    is_trail         = (len(set(ranks)) == 1)
    is_flush         = (len(set(suits)) == 1)
    seq              = is_sequence(values)
    is_pure_sequence = seq and is_flush
    is_pair          = (len(set(ranks)) == 2)

    if is_trail:
        return (1, values)
    if is_pure_sequence:
        return (2, values)
    if seq:
        return (3, values)
    if is_flush:
        return (4, values)
    if is_pair:
        return (5, values)
    return (6, values)

def is_sequence(values):
    """Check for a run of three, allowing A-2-3 low straight."""
    sorted_vals = sorted(values)
    # normal straight
    if sorted_vals == list(range(sorted_vals[0], sorted_vals[0] + 3)):
        return True
    # A-2-3 case (0,1,12)
    return sorted_vals == [0, 1, 12]