from constants import *
from pots import create_pot_collection, POT_TYPES
import numpy as np


class GameState():

    def __init__(self):
        self.phase_number = 1
        self.phase_two_card_number = 1
        self.phase_two_garden_used = "PRIVATE"
        self.player_turn = 1
        self.public_garden = []
        self.player_gardens = {1: [], 2: []}
        self.player_pots = {
            1: create_pot_collection(),
            2: create_pot_collection()}
        self.currently_potting_pot = None
        self.herb_biscuit_player = None
        self.players_skipped = {1: False, 2: False}
        self.deck = create_shuffled_deck()

    def print_results(self):
        print("Player Scores are {}".format(self.get_game_scores()))
        print("Tie breaker scores are {}".format(self.get_tiebreaker_points()))
        print("Winning player is {}!".format(self.get_winning_player()))

    def award_herb_biscuit(self):
        if self.herb_biscuit_player is None:
            self.herb_biscuit_player = self.player_turn

    def get_winning_player(self):
        game_scores = self.get_game_scores()
        if game_scores[0] > game_scores[1]:
            return 1
        if game_scores[1] > game_scores[0]:
            return 2
        tiebreaker_points = self.get_tiebreaker_points()
        if tiebreaker_points[0] > tiebreaker_points[1]:
            return 1
        if tiebreaker_points[1] > tiebreaker_points[0]:
            return 2
        return None

    def get_tiebreaker_points(self):
        player_1_points = self.get_tiebreaker_points_for_player(1)
        player_2_points = self.get_tiebreaker_points_for_player(2)
        return (player_1_points, player_2_points)

    def get_tiebreaker_points_for_player(self, player_num):
        glass_score = self.player_pots[player_num]['GLASS'].get_score()
        herb_biscuit_score = 5 if self.herb_biscuit_player == player_num else 0
        return glass_score + herb_biscuit_score

    def get_game_scores(self):
        player_1_score = self.get_score_for_player(1)
        player_2_score = self.get_score_for_player(2)
        return (player_1_score, player_2_score)

    def get_score_for_player(self, player_num):
        score = 0
        player_pots = self.player_pots[player_num]
        for pot in player_pots:
            score += player_pots[pot].get_score()
        score += len(self.player_gardens[player_num])
        if self.herb_biscuit_player == player_num:
            score += 5
        return score

    def is_game_over(self):
        return self.players_skipped[1] and self.players_skipped[2]

    def set_game_over(self):
        self.players_skipped[1] = True
        self.players_skipped[2] = True

    def remove_plant_from_garden(self, plant, garden_type):
        if garden_type == "PUBLIC":
            self.public_garden.remove(plant)
        else:
            self.player_gardens[self.player_turn].remove(plant)

    def get_available_potting_plants(self):
        return self.public_garden + self.player_gardens[self.player_turn]

    def get_garden_by_type(self, garden_type):
        if garden_type == "PUBLIC":
            return self.public_garden
        else:
            return self.player_gardens[self.player_turn]

    def proceed_to_next_phase(self):
        if self.phase_number == 2:
            # if self.phase_two_card_number == 2:
            self.switch_player_turn()
            self.switch_phase_number()
            # self.switch_phase_two_card_number()
        else:
            if self.is_deck_empty():
                self.switch_player_turn()
            else:
                self.switch_phase_number()

    def is_deck_empty(self):
        return len(self.deck) == 0

    def switch_player_turn(self):
        self.player_turn = 3 - self.player_turn

    def switch_phase_two_card_number(self):
        self.phase_two_card_number = 3 - self.phase_two_card_number

    def switch_phase_number(self):
        self.phase_number = 3 - self.phase_number

    def get_phase_state_vector(self):
        return [self.phase_number - 1]
        #if self.phase_number == 1:
        #    return [1, 0, 0, 0]
        #elif self.phase_two_card_number == 1:
        #    return [0, 1, 0, 0]
        #elif self.phase_two_garden_used == "PUBLIC":
        #    return [0, 0, 1, 0]
        #return [0, 0, 1, 1]

    def get_garden_vector_from_list(self, garden_list):
        vec = []
        for plant in PLANT_TYPES:
            vec += [garden_list.count(plant)]
        return vec

    def get_vec_from_pot_collection(self, pot_collection):
        vec = []
        for pot in POT_TYPES:
            vec += pot_collection[pot].get_vector()
        return vec

    def get_herb_biscuit_vec(self, player_num):
        herb_biscuit_vec = [0, 0]
        if self.herb_biscuit_player == player_num:
            herb_biscuit_vec = [1, 0]
        if self.herb_biscuit_player == 3 - player_num:
            herb_biscuit_vec = [0, 1]
        return herb_biscuit_vec

    def get_players_skipped_vec(self, player_num):
        players_skipped_vec = [0, 0]
        if self.players_skipped[player_num]:
            players_skipped_vec[0] = 1
        if self.players_skipped[3 - player_num]:
            players_skipped_vec[1] = 1
        return players_skipped_vec

    def get_deck_card_vec(self):
        vec = [0 for plant in PLANT_TYPES]
        if self.phase_number == 2:
            if self.phase_two_card_number == 1:
                if len(self.deck) != 0:
                    last_card = self.deck[-1]
                    vec = [int(plant == last_card) for plant in PLANT_TYPES]
        return vec

    def get_state_vector(self, player_num):
        state_vector = []
        # Get Phase vec
        state_vector += self.get_phase_state_vector()
        state_vector += [int(self.player_turn == player_num)]
        state_vector += self.get_garden_vector_from_list(self.public_garden)
        state_vector += self.get_garden_vector_from_list(self.player_gardens[player_num])
        state_vector += self.get_garden_vector_from_list(self.player_gardens[3 - player_num])
        state_vector += self.get_vec_from_pot_collection(self.player_pots[player_num])
        state_vector += self.get_vec_from_pot_collection(self.player_pots[3 - player_num])
        currently_potting_vec = [0, 0, 0, 0]
        if self.currently_potting_pot is not None:
            i = POT_TYPES.index(self.currently_potting_pot)
            currently_potting_vec[i] = 1
        state_vector += currently_potting_vec
        state_vector += self.get_herb_biscuit_vec(player_num)
        state_vector += self.get_players_skipped_vec(player_num)
        state_vector += [len(self.deck) / 48.0]
        state_vector += self.get_deck_card_vec()
        state_vector = np.array(state_vector)
        state_vector = state_vector.reshape(1, len(state_vector))
        return state_vector

    def __str__(self):
        string = ""
        string += "Phase Number is {} \n".format(self.phase_number)
        string += "Phase 2 Card Number is {} \n".format(self.phase_two_card_number)
        string += "Phase 2 garden used is {} \n".format(self.phase_two_garden_used)
        string += "Player Turn is {} \n".format(self.player_turn)
        string += "Public Garden is {} \n".format(self.public_garden)
        string += "Player 1 garden is {} \n".format(self.player_gardens[1])
        string += "Player 2 garden is {} \n".format(self.player_gardens[2])
        string += "Currently plotting {} \n".format(self.currently_potting_pot)
        string += "Herb Biscuit Player is {} \n".format(self.herb_biscuit_player)
        string += "Players Skipped is {} \n".format(self.players_skipped)
        string += "Deck length is {} \n".format(len(self.deck))
        string += "Deck is {} \n".format(self.deck)
        string += "Player 1 pots are {} \n".format(self.player_pots[1])
        string += "Player 2 pots are {} \n".format(self.player_pots[2])
        return string