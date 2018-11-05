import copy
from constants import *


class PlayerAction():
    PHASE_PLAYED = -1

    def is_right_phase(self, game_state):
        if game_state.phase_number == self.PHASE_PLAYED:
            return True
        return False

    def can_perform_action(self, game_state):
        raise NotImplementedError

    def perform_action(self, game_state):
        raise NotImplementedError

    def __repr__(self):
        return str(self)


class PlantAction(PlayerAction):
    PHASE_PLAYED = 2

    def __init__(self, garden_type):
        self.garden_type = garden_type

    def can_perform_action(self, game_state):
        if len(game_state.deck) == 0:
            return False
        if self.is_right_phase(game_state):
            if game_state.phase_two_card_number == 1:
                return True
            if game_state.phase_two_card_number == 2:
                return self.garden_type != game_state.phase_two_garden_used
        return False

    def perform_action(self, old_game_state):
        game_state = copy.deepcopy(old_game_state)
        player_num = game_state.player_turn
        plant = game_state.deck.pop()
        if self.garden_type == "PUBLIC":
            game_state.public_garden += [plant]
        else:
            game_state.player_gardens[player_num] += [plant]
        game_state.phase_two_garden_used = self.garden_type
        game_state.proceed_to_next_phase()
        return game_state

    def __str__(self):
        return "PLANT ACTION {}".format(self.garden_type)


class SkipPottingAction(PlayerAction):
    PHASE_PLAYED = 1

    def can_perform_action(self, game_state):
        if self.is_right_phase(game_state):
            return game_state.currently_potting_pot is None
        return False

    def perform_action(self, old_game_state):
        game_state = copy.deepcopy(old_game_state)
        if game_state.is_deck_empty():
            game_state.players_skipped[game_state.player_turn] = True
        game_state.proceed_to_next_phase()
        return game_state

    def __str__(self):
        return "SKIP POTTING ACTION"


class FinishPlottingAction(PlayerAction):
    PHASE_PLAYED = 1

    def can_perform_action(self, game_state):
        player_num = game_state.player_turn
        if self.is_right_phase(game_state):
            current_pot_label = game_state.currently_potting_pot
            if current_pot_label is not None:
                current_pot = game_state.player_pots[player_num][current_pot_label]
                # print("CURRENT POT IS {}".format(current_pot))
                return current_pot.can_finish_potting()
        return False

    def perform_action(self, old_game_state):
        game_state = copy.deepcopy(old_game_state)
        if game_state.currently_potting_pot == "GLASS":
            current_pot_obj = game_state.player_pots[game_state.player_turn]["GLASS"]
            if current_pot_obj.completes_herb_biscuit():
                game_state.award_herb_biscuit()
        game_state.currently_potting_pot = None
        game_state.proceed_to_next_phase()
        return game_state

    def __str__(self):
        return "FINISH PLOTTING ACTION"


class PotPlantAction(PlayerAction):
    PHASE_PLAYED = 1

    def __init__(self, plant, pot, garden):
        self.plant = plant
        self.pot = pot
        self.garden = garden

    def can_perform_action(self, game_state):
        player_num = game_state.player_turn
        if (self.pot != "GLASS" and self.plant in SPECIAL_PLANTS):
            return False
        if self.is_right_phase(game_state):
            if self.not_potting_somewhere_else(game_state):
                if self.plant in game_state.get_garden_by_type(self.garden):
                    relevant_pot = game_state.player_pots[player_num][self.pot]
                    available_plants = game_state.get_available_potting_plants()
                    if game_state.currently_potting_pot == None and not relevant_pot.is_empty():
                        return False
                    return relevant_pot.can_pot_plant(self.plant, available_plants)
        return False

    def not_potting_somewhere_else(self, game_state):
        player_num = game_state.player_turn
        current_pot_label = game_state.currently_potting_pot
        if current_pot_label is None:
            return True
        else:
            current_pot = game_state.player_pots[player_num][current_pot_label]
            return self.pot == current_pot.TYPE

    def perform_action(self, old_game_state):
        game_state = copy.deepcopy(old_game_state)
        player_num = game_state.player_turn
        game_state.remove_plant_from_garden(self.plant, self.garden)
        game_state.player_pots[player_num][self.pot].pot_plant(self.plant)
        game_state.currently_potting_pot = self.pot
        return game_state

    def __str__(self):
        return "PUT PLANT {} IN POT {} FROM GARDEN {} ACTION".format(self.plant, self.pot, self.garden)


plant_actions = [PlantAction("PRIVATE"), PlantAction("PUBLIC")]
skip_actions = [SkipPottingAction()]
finish_plotting_actions = [FinishPlottingAction()]
potting_actions = []
for garden_type in ['PRIVATE', 'PUBLIC']:
    for pot in ["LARGE", 'WOODEN', 'SMALL', 'GLASS']:
        for plant in PLANT_TYPES:
            potting_actions += [PotPlantAction(plant, pot, garden_type)]

actions = plant_actions + skip_actions + finish_plotting_actions + potting_actions


def get_possible_actions(game_state):
    return [action for action in actions if action.can_perform_action(game_state)]


def get_possible_action_indexes(game_state):
    result = []
    for i in range(len(actions)):
        if actions[i].can_perform_action(game_state):
            result += [i]
    return result
