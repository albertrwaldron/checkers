import numpy as np

class IllegalMove(Exception):
    def __init__(self, message):
        super().__init__(message)


class Board():
    def __init__(self, state=None):
        if state is None:
            state = np.zeros((8,8))
            for row in np.arange(8):
                state[row, ((row+1)%2)::2] = np.nan
                if row < 3:
                    state[row, (row%2)::2] = 1
                if row > 4:
                    state[row, (row%2)::2] = -1
        self.state = state
        self.move_directions = np.array(((1,1), (1, -1), (-1, 1), (-1, -1)))
        self.jump_directions = np.array(((2,2), (2, -2), (-2, 2), (-2, -2)))

    def get_state(self):
        return self.state
    
    def _on_dark(self, row, col):
        return (row+col) % 2 == 0
    
    def _in_bounds(self, row, col):
        return (0 <= row < 8) and (0 <= col < 8)
    
    def _is_opponent(self, piece_value):
        return (self.state != 0) & (np.sign(self.state) != np.sign(piece_value))
    
    def _is_player(self, piece_value):
        return (self.state != 0) & (np.sign(self.state) == np.sign(piece_value))
    
    def _is_empty(self):
        return self.state == 0
    
    def _can_move(self, player):
        is_king = (np.abs(self.state) > 1) * np.ones((4,8,8), dtype=bool)
        moving_forward = (
            self.state * np.ones((4,8,8))) == \
            (np.sign(self.move_directions[:,0]).reshape(4,1,1) * np.ones((4,8,8)))
        allowed_direction = is_king | moving_forward
        can_move = np.zeros((4, 8,8), dtype=bool)
        can_move[0, :-1, :-1] = self._is_player(player)[:-1, :-1] & self._is_empty()[1:, 1:] & allowed_direction[0, :-1, :-1]
        can_move[1, :-1, 1:] = self._is_player(player)[:-1, 1:] & self._is_empty()[1:, :-1] & allowed_direction[1, :-1, 1:]
        can_move[2, 1:, :-1] = self._is_player(player)[1:, :-1] & self._is_empty()[:-1, 1:] & allowed_direction[2, 1:, :-1]
        can_move[3, 1:, 1:] = self._is_player(player)[1:, 1:] & self._is_empty()[:-1, :-1] & allowed_direction[3, 1:, 1:]
        return can_move    
    
    def _can_jump(self, player, coord=None):
        is_king = (np.abs(self.state) > 1) * np.ones((4,8,8), dtype=bool)
        moving_forward = (
            self.state * np.ones((4,8,8))) == \
            (np.sign(self.jump_directions[:,0]).reshape(4,1,1) * np.ones((4,8,8)))
        allowed_direction = is_king | moving_forward
        can_jump = np.zeros((4,8,8), dtype=bool)

        can_jump[0, :-2, :-2] = self._is_player(player)[:-2, :-2] & self._is_empty()[2:, 2:] & allowed_direction[0, :-2, :-2] \
            & self._is_opponent(player)[1:-1, 1:-1]

        can_jump[1, :-2, 2:] = self._is_player(player)[:-2, 2:] & self._is_empty()[2:, :-2] & allowed_direction[1, :-2, 2:] \
            & self._is_opponent(player)[1:-1, 1:-1]

        can_jump[2, 2:, :-2] = self._is_player(player)[2:, :-2] & self._is_empty()[:-2, 2:] & allowed_direction[2, 2:, :-2] \
            & self._is_opponent(player)[1:-1, 1:-1]

        can_jump[3, 2:, 2:] = self._is_player(player)[2:, 2:] & self._is_empty()[:-2, :-2] & allowed_direction[3, 2:, 2:] \
            & self._is_opponent(player)[1:-1, 1:-1]
        if coord is None:
            return can_jump
        else:
            piece_can_jump = np.zeros((4,8,8), dtype=bool)
            piece_row = coord[0]
            piece_col = coord[1]
            piece_can_jump[:, piece_row, piece_col] = can_jump[:, piece_row, piece_col]
            return piece_can_jump
    
    def _is_playable_square(self, from_coord, to_coord):
        from_row, from_col = from_coord
        to_row, to_col = to_coord
        if not self._on_dark(from_row, from_col):
            raise IllegalMove('Attempting to move from a light square.\nPieces are only allowed on the dark squares.')
        if not self._on_dark(to_row, to_col):
            raise IllegalMove('Attempting to move to a light square.\nPieces are only allowed on the dark squares.')
        if not self._in_bounds(from_row, from_row):
            raise IllegalMove('Attempting to move from a square outside the board.')
        if not self._in_bounds(to_row, to_col):
            raise IllegalMove('Attempting to move to a square outside the board.')
        piece_value = self.state[from_row, from_col]
        if piece_value == 0:
            raise IllegalMove('There is no piece to move on this square.')
        if self.state[to_row, to_col] != 0:
            raise IllegalMove('Attempting to move to an occupied square.')
        is_king = np.abs(piece_value) > 1
        if (not is_king) and (np.sign(piece_value) != np.sign(to_row - from_row)):
            raise IllegalMove('Only king pieces can move backwards')

    def move_piece(self, from_coord, to_coord):
        from_row, from_col = from_coord
        to_row, to_col = to_coord
        if np.abs(from_row - to_row) != 1 or np.abs(from_col - to_col) != 1:
            raise IllegalMove('Pieces can only move one square at a time')
        self._is_playable_square(from_coord, to_coord)
        self.state[to_row, to_col] = self.state[from_row, from_col]
        self.state[from_row, from_col] = 0

    def jump_piece(self, from_coord, to_coord):
        from_row, from_col = from_coord
        to_row, to_col = to_coord
        mid_row = from_row + int((to_row - from_row) / 2)
        mid_col = from_col + int((to_col - from_col) / 2)
        if np.abs(from_row - to_row) != 2 or np.abs(from_col - to_col) != 2:
            raise IllegalMove('Jumps must move 2 squares along a diagonal.')
        self._is_playable_square(from_coord, to_coord)
        self.state[to_row, to_col] = self.state[from_row, from_col]
        self.state[mid_row, mid_col] = 0
        self.state[from_row, from_col] = 0

    def calculate_possible_moves(self, player):
        raw_moves = np.argwhere(self._can_move(player))
        from_coords = raw_moves[:, 1:]
        to_coords = from_coords + self.move_directions[raw_moves[:, 0], :]
        return from_coords, to_coords
    
    def calculate_possible_jumps(self, player, coord=None):
        raw_jumps = np.argwhere(self._can_jump(player, coord))
        from_coords = raw_jumps[:, 1:]
        to_coords = from_coords + self.jump_directions[raw_jumps[:, 0], :]
        return from_coords, to_coords
    
    def promote_pieces(self):
        self.state[7, self.state[7, :] == 1] = 1.5
        self.state[0, self.state[0, :] == -1] = -1.5

    def check_winner(self):
        if (self.state > 0).sum() == 0:
            return -1
        elif (self.state < 0).sum() == 0:
            return 1
        else:
            return 0