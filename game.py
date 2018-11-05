import random
from actions import get_possible_actions


def random_player(game_state, possible_actions):
    return random.choice(possible_actions)


def human_player(game_state, possible_actions):
    inp = raw_input("What would you like to do?")
    if (inp == "STOP"):
        raise Exception("You have stopped the game")
    return possible_actions[int(inp)]


class Game:

    def __init__(self):
        self.player1 = random_player
        self.player2 = random_player
        self.log_states = False

    def play_game(self, game_state):
        while not game_state.is_game_over():
            possible_actions = get_possible_actions(game_state)
            if len(possible_actions) > 0:
                if self.log_states:
                    print(game_state)
                print(zip(possible_actions, range(len(possible_actions))))
                print(game_state.get_state_vector(1))
                player_num = game_state.player_turn
                player = self.player1 if player_num == 1 else self.player2
                action = player(game_state, possible_actions)
                game_state = action.perform_action(game_state)
                print("Performed action {}".format(action))
            else:
                print("No actions possible")
                break
        game_state.print_results()
        return game_state