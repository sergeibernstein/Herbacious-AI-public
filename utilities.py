import actions
from actions import get_possible_actions
from game import random_player
from constants import *


def get_gamma(episode_num):
    return 0.99 if episode_num < 1e6 else 0.99


def get_e(episode_num):
    return 0.5 if episode_num < 1e6 else 100000.0/episode_num


def finish_random_player_turn(game_state, network_player_num):
    while (not game_state.is_game_over()) and (game_state.player_turn != network_player_num):
        possible_actions = get_possible_actions(game_state)
        random_action = random_player(game_state, possible_actions)
        game_state = random_action.perform_action(game_state)
    return game_state


def get_reward(game_state, network_player_num):
    reward = 0
    if game_state.is_game_over():
        winner = game_state.get_winning_player()
        if winner == network_player_num:
            reward = WIN_REWARD
        elif winner is None:
            reward = DRAW_REWARD
        else:
            reward = LOSS_REWARD
    return reward


def update_state_and_get_reward(action_index, game_state, network_player_num):
    action = actions.actions[action_index]
    game_state = action.perform_action(game_state)
    game_state = finish_random_player_turn(game_state, network_player_num)
    reward = get_reward(game_state, network_player_num)
    return game_state, reward