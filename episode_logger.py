from constants import *

class EpisodeLogger():

    def __init__(self):
        self.rList = []
        self.lossList = []
        self.legalList = []
        self.networkScoreList = []
        self.opponentScoreList = []
        self.herbBiscuitList = []
        self.card_loss_map = {}
        self.total_game_reward = 0
        self.total_legal_moves = 0
        self.network_score = 0
        self.opponent_score = 0
        self.herbBiscuitFound = 0

    def init_episode(self):
        self.total_game_reward = 0
        self.total_legal_moves = 0
        self.network_score = 0
        self.opponent_score = 0
        self.herbBiscuitFound

    def finish_episode(self, game_state, network_player_num):
        self.network_score = game_state.get_game_scores()[network_player_num - 1]
        self.opponent_score = game_state.get_game_scores()[2 - network_player_num]
        self.herbBiscuitFound = int(game_state.herb_biscuit_player is not None)
        self.total_game_reward = -1
        if game_state.is_game_over():
            if game_state.get_winning_player() == network_player_num:
                self.total_game_reward = WIN_REWARD
            elif game_state.get_winning_player() == 3 - network_player_num:
                self.total_game_reward = LOSS_REWARD
            else:
                self.total_game_reward = DRAW_REWARD
        self.rList.append(self.total_game_reward + 0.0)
        self.legalList.append(self.total_legal_moves + 0.0)
        self.networkScoreList.append(self.network_score + 0.0)
        self.opponentScoreList.append(self.opponent_score + 0.0)
        self.herbBiscuitList.append(self.herbBiscuitFound + 0.0)

    def log_loss(self, loss, card_num):
        self.lossList += [loss]
        if card_num not in self.card_loss_map:
            self.card_loss_map[card_num] = [loss]
        else:
            self.card_loss_map[card_num] += [loss]

    def list_average_split(self, li, split_factor=10):
        for si in range(len(li))[::len(li) / split_factor]:
            print(sum(li[si:si + (len(li) / split_factor)]) / (len(li) / (split_factor + 0.0)))