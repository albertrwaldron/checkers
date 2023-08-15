import pygame
from pygame.locals import QUIT
import sys
import numpy as np
from .constants import *
from IPython.display import clear_output
from time import sleep

class GuiViewer():
    def __init__(self, game):
        self.game = game
        pygame.init()
        self.fps_clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(CAPTION)
        self.last_move_time = pygame.time.get_ticks()
        self.cooldown = 250
        self.selected_piece = None
        self.available_moves = []
        self.winner = 0
        self.available_move_type = None

    def event_loop(self):
        looping = True
        while looping:
            active_player = self.game.get_active_player()
            active_player_type = active_player.player_type
            for event in pygame.event.get():
                if event.type == QUIT:
                    looping = False
                if (active_player_type == 'interactive') and event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())
            if (self.winner == 0) and active_player_type == 'ai':
                now = pygame.time.get_ticks()
                if now - self.last_move_time >= self.cooldown:
                    self.last_move_time = now
                    move_type, move = active_player.determine_move(self.game)
                    self.winner = self.game.play_turn(move_type, move)
            self.window.fill(BACKGROUND)
            self.draw_board()
            pygame.display.update()
            self.fps_clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def draw_board(self):
        def draw_square(color, row, col):
            pygame.draw.rect(self.window, color, 
                                     (col*SQUARE_WIDTH, 
                                      row*SQUARE_HEIGHT, 
                                      SQUARE_WIDTH, 
                                      SQUARE_HEIGHT))
        def draw_piece(color, row, col, king=False):
            center = (col*SQUARE_WIDTH + SQUARE_WIDTH//2,
                      row*SQUARE_HEIGHT + SQUARE_HEIGHT//2)
            pygame.draw.circle(self.window, color, center, SQUARE_HEIGHT//3)
            if self.selected_piece is not None and self.selected_piece == (row, col):
                pygame.draw.circle(self.window, HIGHLIGHT_COLOR, center, SQUARE_HEIGHT//3, 3)
            if king:
                k_font = pygame.font.Font('freesansbold.ttf', 24)
                k_text = k_font.render('K', color, (255, 255, 255))
                k_rect = k_text.get_rect()
                k_rect.center = center
                self.window.blit(k_text, k_rect)
        def draw_candidates(chain):
            for (row, col) in chain:
                center = (col*SQUARE_WIDTH + SQUARE_WIDTH//2,
                      row*SQUARE_HEIGHT + SQUARE_HEIGHT//2)
                pygame.draw.circle(self.window, HIGHLIGHT_COLOR, center, CANDIDATE_RADIUS)
        for row in range(8):
            for col in range(8):
                square_state = self.game.board.state[row, col]
                king = np.abs(square_state) > 1
                if np.isnan(square_state):
                    draw_square(LIGHT_SQUARE_COLOR, row, col)
                else:
                    draw_square(DARK_SQUARE_COLOR, row, col)
                    if square_state > 0:
                        draw_piece(PLAYER_1_COLOR, row, col, king)
                    elif square_state < 0:
                        draw_piece(PLAYER_2_COLOR, row, col, king)
        for chain in self.available_moves:
            draw_candidates(chain)
    
    def handle_click(self, coord):
        if self.winner != 0:
            return self.winner
        click_x, click_y = coord
        click_col = click_x // SQUARE_WIDTH
        click_row = click_y // SQUARE_HEIGHT
        selected_state = self.game.board.state[click_row, click_col]
        if np.sign(selected_state) == np.sign(self.game.turn):
            self.selected_piece = (click_row, click_col)
            legal_moves = self.game.determine_legal_moves()
            self.available_move_type = legal_moves[0]
            self.available_moves = [[tuple(a) for a in m[1:]] for m in legal_moves[1] if tuple(m[0]) == (click_row, click_col)]
        for available_move in self.available_moves:
            if (click_row, click_col) == available_move[-1]:
                self.winner = self.game.play_turn(self.available_move_type, [self.selected_piece] + available_move)
                self.selected_piece = None
                self.available_move_type = None
                self.available_moves = []
                self.last_move_time = pygame.time.get_ticks()


class NotebookGameViewer():
    def __init__(self, game):
        self.game = game

    def draw_board(self):
        clear_output(wait=True)
        sleep(0.5)
        print(self.game.board.state)

    def wait_for_input(self):
        print(f'It is player {self.game.turn}\'s turn.')
        move_type, available_moves = self.game.determine_legal_moves()
        print(f'''Only "{move_type} are available. Choose one of the following:''')
        for i, move in enumerate(available_moves):
            print(f'{i}): {[tuple(m) for m in move]}')
        sleep(0.5)
        chosen_move = 0
        while 0 <= chosen_move < len(available_moves):
            user_input = input("Enter your choice (q to quit game): ")
            if user_input.lower()[0] in 'qe':
                return None, None
            chosen_move = int(user_input)
        return move_type, available_moves[chosen_move]
    
    def event_loop(self):
        winner = 0
        move_type, move = 'start game', 'board initialized'
        while winner == 0:
            self.draw_board()
            print(f'last move was a "{move_type}": {move}')
            player = self.game.get_active_player()
            if player.player_type == 'ai':
                sleep(1)
                move_type, move = player.determine_move(self.game)
                
            elif player.player_type == 'interactive':
                move_type, move = self.wait_for_input()
                if (move_type, move) == (None, None):
                    break
            winner = self.game.play_turn(move_type, move)
            self.draw_board()
            print(f'Game Over! Player {winner} has won!')