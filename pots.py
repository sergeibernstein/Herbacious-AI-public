from constants import *


class Pot:
    SCORE_MAP = {}
    TYPE = None
    CAN_HOLD_SPECIAL = False

    def __init__(self):
        self.potted_plants = []
        self.finished_potting = False

    def is_empty(self):
        return len(self.potted_plants) == 0

    def get_score(self):
        return self.SCORE_MAP.get(len(self.potted_plants), 0)

    def pot_plant(self, plant):
        self.potted_plants += [plant]

    def get_vector(self):
        vec = []
        if self.CAN_HOLD_SPECIAL:
            for plant in PLANT_TYPES:
                vec += [self.potted_plants.count(plant)]
        else:
            for plant in NON_SPECIAL_PLANTS:
                vec += [self.potted_plants.count(plant)]
        return vec

    # available_plants includes the plant!!
    def can_pot_plant(self, plant, available_plants):
        raise NotImplementedError

    def can_finish_potting(self):
        return len(self.potted_plants) > 0

    def __str__(self):
        return str(self.potted_plants)

    def __repr__(self):
        return str(self.potted_plants)


class LargePot(Pot):
    SCORE_MAP = {
        0: 0,
        1: 2,
        2: 6,
        3: 10,
        4: 14,
        5: 18,
        6: 20,
        7: 22
    }
    TYPE = "LARGE"

    def can_pot_plant(self, plant, available_plants):
        if len(self.potted_plants) == 0:
            return True
        return plant == self.potted_plants[0]


class WoodenPot(Pot):
    SCORE_MAP = {
        0: 0,
        2: 3,
        3: 4,
        4: 6,
        5: 8,
        6: 12,
        7: 14
    }
    TYPE = "WOODEN"

    def can_pot_plant(self, plant, available_plants):
        pot_space_available = plant not in self.potted_plants
        another_plant_available = True
        if (len(self.potted_plants) == 0):
            another_plant_available = False
            for available_plant in available_plants:
                if (available_plant not in SPECIAL_PLANTS and available_plant != plant):
                    another_plant_available = True
        return pot_space_available and another_plant_available

    def can_finish_potting(self):
        return len(self.potted_plants) >= 2


class SmallPot(Pot):
    SCORE_MAP = {
        0: 0,
        2: 4,
        4: 8,
        6: 12,
        8: 14,
        10: 16,
        12: 18,
        14: 18
    }
    TYPE = "SMALL"

    def can_pot_plant(self, plant, available_plants):
        times_plant_already_in_pot = self.potted_plants.count(plant)
        pot_space_available = times_plant_already_in_pot < 2
        another_plant_available = True
        if (times_plant_already_in_pot == 0 and available_plants.count(plant) == 1):
            another_plant_available = False
        return pot_space_available and another_plant_available

    def can_finish_potting(self):
        num_potted_plants = len(self.potted_plants)
        if num_potted_plants == 0:
            return False
        for plant in set(self.potted_plants):
            if self.potted_plants.count(plant) % 2 == 1:
                return False
        return True


class GlassPot(Pot):
    SCORE_MAP = {
        0: 0,
        1: 2,
        2: 4,
        3: 6
    }
    TYPE = "GLASS"
    CAN_HOLD_SPECIAL = True

    def get_score(self):
        raw_score = self.SCORE_MAP[len(self.potted_plants)]
        special_score = 0
        special_score += self.potted_plants.count("Mint")
        special_score += self.potted_plants.count("Chive") * 2
        special_score += self.potted_plants.count("Thyme") * 3
        return raw_score + special_score

    def is_pot_full(self):
        return len(self.potted_plants) == 3

    def completes_herb_biscuit(self):
        if not self.is_pot_full():
            return False
        for herb in SPECIAL_PLANTS:
            if herb not in self.potted_plants:
                return False
        return True

    def can_pot_plant(self, plant, available_plants):
        if len(available_plants) == 0:
            return False
        return not self.is_pot_full()


def create_pot_collection():
    pot_collection = {
        "LARGE": LargePot(),
        "WOODEN": WoodenPot(),
        "SMALL": SmallPot(),
        "GLASS": GlassPot()
    }
    return pot_collection


POT_TYPES = ["LARGE", "WOODEN", "SMALL", "GLASS"]