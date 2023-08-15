# Checkers Game

This is a very basic implementation of the classic board game, Checkers.

## Rules of Checkers
- Players take turns moving one piece at a time.
- Pieces can move one space at a time on the dark squares of the board.
- Pieces can jump opposing pieces if there is an opposing piece on an adjacent square and the next square along the diagonal is empty.
    - If a jumps are available on your turn a jump must be played.
    - Jumps can be chained. If subsequent jumps are available after a jump _with the same piece as the original jump_ these jumps can be taken as well. (The additional jumps are also mandatory.)
- Pieces are only allowed to move and jump forward (unless they are a king).
- Peices are promoted to kings when they reach the opposite side of the board as their starting squares.

## Setup of the game

Prerequisites: Conda is installed on your machine

1. Clone this reposirory and switch your working directory to the repository root
2. Set up the proper python environment
  - `conda env create -f environment.yaml`
  - `conda activate checkers`

## Running the game
1. With the working directory and conda environment from the setup simply execute the command `python main.py`

## Playing the game

You will be the red pieces. The black pieces will be played by a computer player which decides its moves based on the Minimax algorithm.