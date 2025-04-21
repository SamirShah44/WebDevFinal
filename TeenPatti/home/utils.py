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
    rank_order = {r: i for i, r in enumerate(RANKS)}
    values = sorted([rank_order[c[:-1]] for c in hand], reverse=True)
    return sum(values)
