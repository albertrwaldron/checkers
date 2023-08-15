from .board import Board

class Game():
    def __init__(self, player1, player2):
        self.board = Board()
        self.turn = 1
        self.players = {1: player1, -1:player2}

    def get_active_player(self):
        return self.players[self.turn]
    
    def flatten_dict(self, d, out, prior=None):
        if not isinstance(d, dict):
            out.append(prior.copy() + [d])
        else:
            if prior is None:
                prior = []
            for k, v in d.items():
                self.flatten_dict(v, out, prior.copy() + [k[1]])

    def determine_legal_moves(self):
        return self._determine_legal_moves(self.board)
    
    def _determine_legal_moves(self, board):
        jump_pieces, jump_targets = board.calculate_possible_jumps(self.turn)
        if jump_pieces.shape[0] > 0:
            jump_chain = self.calculate_jump_chain(jump_pieces, jump_targets, self.board, self.turn)
            moves = []
            self.flatten_dict(jump_chain, moves)
            return 'jump', moves
        else:
            return 'move', list(zip(*board.calculate_possible_moves(self.turn)))

    def calculate_jump_chain(self, move_pieces, move_targets, board, player):
        from copy import deepcopy
        if move_pieces.shape[0] == 0:
            return None
        chain = {}
        for i, target in enumerate(move_targets):
            temp_board = deepcopy(board)
            piece = move_pieces[i,:]
            temp_board.jump_piece(piece, target)
            temp_pieces, temp_targets = temp_board.calculate_possible_jumps(player, target)
            next_move = self.calculate_jump_chain(temp_pieces, temp_targets, temp_board, player)
            chain[(i, tuple(piece))] = next_move if next_move is not None else tuple(target)
        return chain           
    
    def play_turn(self, move_type, move):
        if move_type == 'move':
            self.board.move_piece(*move)
        else:
            for _move in zip(move[:-1], move[1:]):
                self.board.jump_piece(*_move)
        self.board.promote_pieces()
        self.turn *= -1
        return self.board.check_winner()