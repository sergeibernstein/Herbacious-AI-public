from random import shuffle

LOSS_REWARD = 0.1
DRAW_REWARD = 0.5
WIN_REWARD = 1.0

herb_counts = {
    "Dill":9,
    "Bay":9,
    "Rosemary":9,
    "Saffron":9,
    "Sage":9,
    "Lavender":9,
    "Tarragon":9,
    "Mint":3,
    "Chive":3,
    "Thyme":3
}

PLANT_TYPES = ['Dill', 'Tarragon', 'Sage', 'Rosemary', 'Lavender', 'Saffron', 'Bay','Mint','Chive','Thyme']
SPECIAL_PLANTS = ['Mint','Chive','Thyme']
NON_SPECIAL_PLANTS = [x for x in PLANT_TYPES]
for plant in SPECIAL_PLANTS:
    NON_SPECIAL_PLANTS.remove(plant)


def create_shuffled_deck():
    num_cards = 72 - 24
    deck = []
    for herb in herb_counts:
        for i in range(herb_counts[herb]):
            deck += [herb]
    shuffle(deck)
    return deck[:num_cards]