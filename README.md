
# Tetris AI
Uses an evolutionary approach to teach an AI how to play the classic game of Tetris
## Example
![Example Snake](https://github.com/FrankWan27/TetrisAI/blob/master/img/exampletetris.gif?raw=true)

[Click Here](#training-example) for more example videos

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Controls](#controls)
- [Neural Network Structure](#neural-network-structure)
- [Optimizations](#optimizations)
- [Training Example](#training-example)
- [Authors](#authors)

---
## Overview

### Game Rules

Following a standard set of Tetris rules:
1. The game is over if your pieces reach the top of the screen
2. The player gets one point for each line the current Tetris piece is dropped (optional)
3. The player can remove pieces from the screen by filling all the blank space in one or more lines
	- 1 Line  = 100 points
	- 2 Lines = 400 points
	- 3 Lines = 1500 points
	- 4 Lines = 3200 points
---
## Installation

### Clone

- Clone this repo to your local machine using `git clone https://github.com/FrankWan27/TetrisAI.git`

### Dependencies

- [Python 3 ](https://www.python.org/downloads/)
- [Pygame](https://www.pygame.org/)  - used to render graphics
  ```pip install pygame```
- [Numpy](https://numpy.org/) - used for matrix manipulation in numpy.ndarray
  ```pip install numpy```
### Usage
To start running the Tetris game, simply run main.py in the parent directory

 ```python main.py```
 
 To continue running the snake AI from a saved neural network state, add the textfile as an argument
 
 ```python main.py "./nnets/7 inputs 238 efficiency"```

---

## Controls
The game can be played by the AI (AI Mode) or by a human (Human Mode). By default, the game starts in AI mode. Upon closing the game by clicking the X button, the best performing snake's neural network will be written to the file "BestOnClose.txt"

### AI Mode

- Q/E - Increase/Decrease the speed setting (Slow, Normal, Fast, Fastest)
- L - Immediately kill the current neural network
- W - Write best performing Tetris neural network to the file "BestOnManual.txt"
- B - Show/Hide debug info
- P - Switch to Human Mode

### Human Mode

- Left/Right Arrow Key - Move current piece left/right
- Up Arrow Key - Rotate current piece
- Down Array Key - Soft drop piece one line
- Left Shift - Move current piece to hold
- Space - Fast drop current piece
- P - Switch to AI Mode

## Neural Network Structure

This neural network is 7x4x2x1, with one input layer, two hidden layers, and one output layer. 
![Neural Net](https://github.com/FrankWan27/TetrisAI/blob/master/img/nnet.png?raw=true)

Each input is a heuristic extracted from the current board state + current potential move. 

1. Line Clear Score - How many points are obtained by line clears on this move
2. Roughness - Total difference in heights between adjacent columns
3. Weighted Height - Height of the tallest column (weighted to emphasize taller heights)
4. Range of Heights - Range of heights between all columns
5. Cumulative Heights - Total height of all columns added together
6. Number of Holes - Total number of holes that exist on the board
7. Deepest Well - The depth of the deepest well currently on the board

### Holes
A hole is defined by an empty block that is covered by a piece above it. Below is an example of a board with 11 holes.
![11 Holes](https://github.com/FrankWan27/TetrisAI/blob/master/img/hole.png?raw=true)
### Wells
A well is defined by a contiguous vertical column of empty blocks which is surrounded by solid blocks and is not covered. Below is an example of a well with depth of 3.
![3 Well](https://github.com/FrankWan27/TetrisAI/blob/master/img/well.png?raw=true)

### Decision Making
Every time the player gets a new piece, the neural network will be given the 7 input heuristics after every possible move (including swapping with the held piece). Based on the neural network's weights, it will assign a rating to every possible move and perform the highest rated move. 

## Optimizations
The Tetris AI was quickly able to learn how to survive indefinitely by optimizing the roughness of the board and making one-line clears whenever possible. However, this approach is very score inefficient and so we tried many ways to optimize the strategy of the AI to score more points with fewer moves. 

### Our target
To establish a baseline, first we calculated the minimum and maximum possible score efficiency. If we clear 10 pieces worth of blocks, that's 10 x 4 blocks total, which is exactly equal to 4 lines. There are only 5 ways to clear 4 lines:
1. 4 one-line clears = 4 x 100 pts / 10 pieces = 40 pts/piece 
2. 1 two-line clear and 2 one-line clears = (400 pts + 2 x 100 pts) / 10 pieces = 60 pts/piece
3. 2 two-line clears = 2 x 400 pts / 10 pieces = 80 pts/piece
4. 1 three-line clear and 1 one-line clear = (1500 pts + 100 pts) / 10 pieces = 160 pts/piece
5. 1 four-line clear = 3200 pts / 10 pieces = 320 pts/piece

From these calculations we can see that the minimum and maximum score efficiency is 40 pts/piece and 320 pts/piece respectively.  With the Tetris AI only focused on survival, it was able to achieve a score efficiency of 46.5 pts/piece. 

For comparison, when I manually play the game and prioritize only getting four-line clears, I was able to achieve a score efficiency of 223 pts/piece. 

### Avoid One-Line Clears

By introducing a priority system, we were able to assign priorities to certain moves to consider. To start, we lowered the priority for the lowest scoring move (one-line clears), which means the neural network will only consider performing a one-line clear if there is no other move it can possibly make. This improved the score efficiency of the AI greatly, increasing it to around 100 pts/piece. 

### Avoid Making Holes

By avoiding one-line clears, the AI would prioritize creating a hole over clearing a single line, which was undesired behavior. To avoid this, we also lowered the priority for any move that would result in one or more holes. This change resulted in the first time Tetris AI's score efficiency went over 200 pts/piece. 

### Panic Mode

Following the above priorities made the Tetris AI susceptible to dying, so we introduced a panic mode which disables priorities if the tallest column height is above 12. This change resulted in the highest recorded score efficiency of 238 pts/piece, surpassing my baseline manual score efficiency. 

## Training Example 

This is an example of the Tetris AI optimizing for high score efficiency.
![training](https://github.com/FrankWan27/TetrisAI/blob/master/img/efficienttetris.gif?raw=true)
---

## Authors

* **Frank Wan** - [Github](https://github.com/FrankWan27)
