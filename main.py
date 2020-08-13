import random
import tetrisAI as TetrisAI
import sys

#random.seed(0)
if len(sys.argv) > 1:
	TetrisAI.startGame(sys.argv[1])
else:
	TetrisAI.startGame()
