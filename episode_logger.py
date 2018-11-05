class EpisodeLogger():

    def __init__(self):
        self.rList = []
        self.lossList = []
        self.legalList = []
        self.networkScoreList = []
        self.opponentScoreList = []
        self.herbBiscuitList = []
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
        self.rList.append(self.total_game_reward + 0.0)
        self.legalList.append(self.total_legal_moves + 0.0)
        self.networkScoreList.append(self.network_score + 0.0)
        self.opponentScoreList.append(self.opponent_score + 0.0)
        self.herbBiscuitList.append(self.herbBiscuitFound + 0.0)