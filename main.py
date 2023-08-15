from checkers import Game, InteractivePlayer, RandomPlayer, MinimaxPlayer, GuiViewer

if __name__ == '__main__':
    player_1 = InteractivePlayer()
    player_2 = MinimaxPlayer(7, False)
    game = Game(player_1, player_2)
    viewer = GuiViewer(game)
    viewer.event_loop()