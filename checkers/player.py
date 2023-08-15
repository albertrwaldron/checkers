from copy import deepcopy
import numpy as np

class InteractivePlayer():
    def __init__(self):
        self.player_type = 'interactive'

class RandomPlayer():
    def __init__(self):
        self.player_type = 'ai'

    def determine_move(self, game):
        from random import choice
        move_type, available_moves = game.determine_legal_moves()
        return move_type, choice(available_moves)
    
class MinimaxPlayer():
    def __init__(self, max_depth=1, maximize=False):
        self.player_type = 'ai'
        self.max_depth = max_depth
        self.maximize = maximize

    def score_board(self, board):
        if (board.state > 0).sum() == 0:
            return -np.inf
        if (board.state < 0).sum() == 0:
            return np.inf
        return np.nansum(board.state)
    
    def determine_move(self, game):
        def minimax(game, maximize, depth, alpha, beta):
            from random import shuffle
            try:
                score = self.score_board(game.board)
                if (depth >= self.max_depth) or np.isinf(score):
                    return score
                move_type, available_moves = game.determine_legal_moves()
                shuffle(available_moves)
                if maximize:
                    if available_moves == []:
                        return -np.inf
                    max_idx = None
                    value = -np.inf
                    for idx, move in enumerate(available_moves):
                        game_cp = deepcopy(game)
                        game_cp.play_turn(move_type, move)
                        mm = minimax(game_cp, False, depth+1, alpha, beta)
                        if mm >= value:
                            max_idx = idx
                        value = max((value, mm))
                        alpha = max((value, alpha))
                        if value >= beta:
                            # break
                            pass
                    if depth == 1:
                        return move_type, available_moves[max_idx]
                    else:
                        return value
                else:
                    if available_moves == []:
                        return np.inf
                    min_idx = None
                    value = np.inf
                    for idx, move in enumerate(available_moves):
                        game_cp = deepcopy(game)
                        game_cp.play_turn(move_type, move)
                        mm = minimax(game_cp, True, depth+1, alpha, beta)
                        if mm <= value:
                            min_idx = idx
                        value = min((value, mm))
                        beta = min((value, beta))
                        if value <= alpha:
                            # break
                            pass
                    if depth == 1:
                        print(f'Computer evaluation: {value}')
                        print(f'Move type: {move_type}')
                        print(f'Chosen move: {available_moves[min_idx]}')
                        return move_type, available_moves[min_idx]
                    else:
                        return value
            except:
                print(f'move_type: {move_type}')
                print(f'available_moves: {available_moves}')
                print(f'depth: {depth}')
                print(game_cp.board.state)
                raise
        
        return minimax(game, self.maximize, 1, -np.inf, np.inf)