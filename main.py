import random
import tetrisAI as TetrisAI
import snakeAI as SnakeAI
import sys

random.seed(0)

#TetrisAI.startGame()
if len(sys.argv) > 1:
	SnakeAI.startGame(sys.argv[1])
else:
	SnakeAI.startGame()
