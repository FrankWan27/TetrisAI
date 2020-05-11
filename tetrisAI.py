#import necessary libraries
#pip install pygame
import pygame
import numpy as np
import random
import os
import sys
from shape import Shape
from nnet import Nnets
from defs import *

# PyInstaller adds this attribute
if getattr(sys, 'frozen', False):
    # Running in a bundle
    CurrentPath = sys._MEIPASS
else:
    # Running in normal Python environment
    CurrentPath = os.path.dirname(__file__)




#setup global vars
gameDisplay = ''
grid = np.zeros((10, 20))

#official shape and orientation
#https://tetris.wiki/Super_Rotation_System
#changed to be row based and 4x4

speeds = [FPS * 8, FPS * 2, 1]
speedSetting = 2
held = ''
player = False
holdUsed = False
currentShape = Shape()
upcoming = []
ticker = 0
score = 0
forceMove = 0

suisei = Nnets(Species.TETRIS)

#Core game loop
def startGame():
    global gameDisplay
    global ticker
    global currentShape
    global forceMove
    pygame.init()
    gameDisplay = pygame.display.set_mode((600, 800))
    pygame.display.set_caption('Tetris AI')
    bg = pygame.image.load(os.path.join(CurrentPath, 'img/BG.png'))
    resetGame()

    currentShape = getNextShape()
    addShape()

    runloop = True
    clock = pygame.time.Clock()
    
    dt = 0
    gameTime = 0
    ticker = 0

    suisei.createPop()

    while runloop:        
        #Break loop if we quit
        runloop = handleInput()
        #Get AI's best move
        if not player:
            doBestMove(getBestMove())

        dt = clock.tick(FPS)
        gameTime += dt
        ticker += dt
        if(ticker >= speeds[speedSetting%3]):
            forceMove += 1
            moveDown()
            ticker = 0

        if forceMove >= 60:
            fastDrop()

        #Draw everything to screen
        gameDisplay.blit(bg, (0, 0))
        showDebug(dt, gameTime)
        showScore()
        showNext()
        showHeld()
        showGrid()
        
        pygame.display.update()

    pygame.display.quit()
    pygame.quit()



def resetGame():
    global grid
    global held
    global upcoming
    global score

    grid = np.zeros((10, 20))
    held = ''
    upcoming = generateUpcoming()
    score = 0

def showLabel(data, text, x, y):
    font = pygame.font.Font(os.path.join(CurrentPath, 'fonts/abel.ttf'), 20)
    label = font.render('{} {}'.format(text, data), 1, (40,40,250))
    gameDisplay.blit(label, (x, y))
    return y + 20

def showDebug(dt, gameTime):
    xOffset = 10
    yOffset = 2
    yOffset = showLabel(round(1000/dt, 2), 'FPS: ', xOffset, yOffset)
    #yOffset = showLabel(round(gameTime/1000, 2),'Game Time: ', xOffset, yOffset)
    yOffset = showLabel(suisei.generation, 'Current Generation: ', xOffset, yOffset)
    yOffset = showLabel(suisei.currentNnet, 'Current Nnet: ', xOffset, yOffset)
    yOffset = showLabel(suisei.highestGen, 'Best Gen So Far: ', xOffset, yOffset)

    yOffset += 628
    yOffset = showLabel(int(suisei.genAvg), 'Current Gen Average: ', xOffset, yOffset)
    yOffset = showLabel(int(suisei.deltaAvg), 'Change From Last Gen: ', xOffset, yOffset)
    yOffset = showLabel(suisei.highscore, 'Highscore (This Gen): ', xOffset, yOffset)
    yOffset = showLabel(suisei.highestScore, 'Highest Score So Far: ', xOffset, yOffset)

def showScore():
    font = pygame.font.Font(os.path.join(CurrentPath, 'fonts/abel.ttf'), 80)
    label = font.render('{}'.format(score), 1, (0, 0, 0))
    offset = font.size('{}'.format(score))
    gameDisplay.blit(label, (390 - offset[0], 707))

def showGrid():
    xOffset = 150
    yOffset = 99
    for x in range(grid.shape[0]):
        for y in range(grid.shape[1]):
            if(grid[x][y] != 0):
                pygame.draw.rect(gameDisplay, pygame.Color('white'), (xOffset + x * 30, yOffset + y * 30, 30, 30))
                pygame.draw.rect(gameDisplay, pygame.Color(colors[grid[x][y]]), (1 + xOffset + x * 30, 1 + yOffset + y * 30, 28, 28))

#Show next 4 blocks
def showNext():
    xOffset = 475
    yBase = 215
    yOffset = 125

    for i in range(4):
        if i == 1:
            xOffset -= 5
            yOffset -= 5
        nextShape = createShape(upcoming[i])

        for rect in nextShape:
            pygame.draw.rect(gameDisplay, pygame.Color('white'), rect.move(xOffset, yBase +  yOffset * i))
            pygame.draw.rect(gameDisplay, pygame.Color(colors[upcoming[i]]), (1 + xOffset + rect.x, 1 + yBase + yOffset * i + rect.y, rect.width - 2, rect.height - 2))   

#Show held block
def showHeld():
    xOffset = 35
    yOffset = 215

    if held != '':
        nextShape = createShape(held)
        for rect in nextShape:
            pygame.draw.rect(gameDisplay, pygame.Color('white'), rect.move(xOffset, yOffset))
            pygame.draw.rect(gameDisplay, pygame.Color(colors[held]), (1 + xOffset + rect.x, 1 + yOffset + rect.y, rect.width - 2, rect.height - 2))   

def createShape(shape):
    rectList = []
    for x in range(len(shapes[shape])):
        for y in range(len(shapes[shape][0])):
            if shapes[shape][x][y] == 1:
                rectList.append(pygame.Rect(x * 22, y * 22, 22, 22))
            elif shapes[shape][x][y] == 4:
                rectList.append(pygame.Rect(14 + x * 30 - 30, y * 30 - 30, 30, 30))
            elif shapes[shape][x][y] != 0:
                rectList.append(pygame.Rect(x * 30, y * 30, 30, 30))
    return rectList

#Handle keyboard input
def handleInput():
    global speedSetting
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    speedSetting += 1
                if event.key == pygame.K_q:
                    speedSetting -= 1
                if player:
                    if event.key == pygame.K_LEFT:
                        moveLeft()
                    if event.key == pygame.K_RIGHT:
                        moveRight()
                    if event.key == pygame.K_z:
                        rotateLeft()
                    if event.key == pygame.K_x:
                        rotateRight()
                    if event.key == pygame.K_DOWN:
                        moveDown()
                    if event.key == pygame.K_UP:
                        rotateRight()
                    if event.key == pygame.K_SPACE:
                        fastDrop()
                    if event.key == pygame.K_LSHIFT:
                        hold()


    return True


#Adds currentShape to the grid
def addShape():
    for x in range(len(currentShape.shape)):
        for y in range(len(currentShape.shape[0])):
            if currentShape.shape[x][y] != 0:
                grid[currentShape.x + x][currentShape.y + y] = currentShape.shape[x][y];

#Removes currentShape from the grid
def removeShape():
    for x in range(len(currentShape.shape)):
        for y in range(len(currentShape.shape[0])):
            if currentShape.shape[x][y] != 0:
                grid[currentShape.x + x][currentShape.y + y] = 0;


#Move currentShape left 1 tile
def moveLeft():
    removeShape()
    currentShape.x -= 1
    if checkCollision(currentShape):
        currentShape.x += 1
    addShape()

#Move currentShape right 1 tile
def moveRight():
    removeShape()
    currentShape.x += 1
    if checkCollision(currentShape):
        currentShape.x -= 1
    addShape()

#Rotate currentShape left
def rotateLeft():
    global currentShape
    removeShape()
    currentShape.shape = rotateShape(currentShape, 3)
    if checkWallKick(currentShape, -1):
        currentShape.shape = rotateShape(currentShape, 1)
        currentShape.rotation += 1
    currentShape.rotation -= 1
    addShape()

#Rotate currentShape right
def rotateRight():
    global currentShape
    removeShape()
    currentShape.shape = rotateShape(currentShape, 1)


    if checkWallKick(currentShape, 1):
        currentShape.shape = rotateShape(currentShape, 3)
        currentShape.rotation -= 1
    currentShape.rotation += 1
    addShape()

#Returns True if all wall kicks fail
def checkWallKick(currentShape, direction):
    rot = currentShape.rotation%4

    #https://tetris.wiki/Super_Rotation_System#Wall_Kicks
    restKicks = {
        'oToR':[(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        'rToO':[(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        'rToF':[(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
        'fToR':[(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
        'fToL':[(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
        'lToF':[(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        'lToO':[(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
        'oToL':[(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)]
    }
    iKicks = {
        'oToR':[(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        'rToO':[(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        'rToF':[(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
        'fToR':[(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        'fToL':[(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
        'lToF':[(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
        'lToO':[(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
        'oToL':[(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)]
    }

    code = ''
    if rot == 0 and direction == 1:
        code = 'oToR'
    elif rot == 1 and direction == -1:
        code = 'rToO'
    elif rot == 1 and direction == 1:
        code = 'rToF'
    elif rot == 2 and direction == -1:
        code = 'fToR'
    elif rot == 2 and direction == 1:
        code = 'fToL'
    elif rot == 3 and direction == -1:
        code = 'lToF'
    elif rot == 3 and direction == 1:
        code = 'lToO'
    elif rot == 0 and direction == -1:
        code = 'oToL'
    else:
        print('Invalid Rotation!')
        code = 'oToR'

    if currentShape.letter == 'O':
        return False
    elif currentShape.letter == 'I':
        for kick in iKicks[code]:
            currentShape.x += kick[0]
            currentShape.y += kick[1]
            if not checkCollision(currentShape):
                return False
            currentShape.x -= kick[0]
            currentShape.y -= kick[1]
    else:
        for kick in restKicks[code]:
            currentShape.x += kick[0]
            currentShape.y += kick[1]
            if not checkCollision(currentShape):
                return False
            currentShape.x -= kick[0]
            currentShape.y -= kick[1]

    return True




def rotateShape(currentShape, rotations):

    shape = currentShape.shape

    if not (currentShape.letter == 'I' or currentShape.letter == 'O'):
        shape = currentShape.shape[0:3][0:3]

    for i in range(rotations):
        for x in range(0, int(len(shape) / 2)): 
            for y in range(x, len(shape) - x - 1): 
                temp = shape[x][y] 
                shape[x][y] = shape[y][len(shape) - x - 1] 
                shape[y][len(shape) - x - 1] = shape[len(shape) - x - 1][len(shape) - y - 1] 
                shape[len(shape) - x - 1][len(shape) - y - 1] = shape[len(shape) - y - 1][x] 
                shape[len(shape) - y - 1][x] = temp 

    if not (currentShape.letter == 'I' or currentShape.letter == 'O'):
        zeros = [[0 for i in range(4)] for j in range(4)]
        for i in range(3):
            for j in range(3):
                zeros[i][j] = shape[i][j]
        shape = zeros
    return shape

#Move currentShape right 1 tile
def moveDown():
    global currentShape
    global score
    removeShape()
    currentShape.y += 1
    if checkCollision(currentShape):
        currentShape.y -= 1
        addShape()
        clearRows()
        currentShape = getNextShape()
        #check if we lost
        if checkCollision(currentShape):
            handleLoss()

    score += 1
    addShape()

#Hold currentShape
def hold():
    global currentShape
    global held
    global holdUsed

    if(holdUsed):
        return

    removeShape()
    if(held == ''):
        held = currentShape.letter
        currentShape = getNextShape()
    else:
        temp = held
        held = currentShape.letter
        currentShape = Shape(temp)
        currentShape.x = (int)(len(grid) / 2 - len(currentShape.shape) / 2)

    holdUsed = True
    addShape()


#Move currentShape to the bottom
def fastDrop():
    global currentShape
    global score
    removeShape()
    while not checkCollision(currentShape):
        currentShape.y += 1
        score += 2

    
    currentShape.y -= 1
    score -= 2
    addShape()
    clearRows()
    currentShape = getNextShape()
    #check if we lost
    if checkCollision(currentShape):
        handleLoss()

    addShape()

#Checks if currentShape collides with boundary or other blocks
def checkCollision(currentShape):
    for x in range(len(currentShape.shape)):
        for y in range(len(currentShape.shape[0])):
            if currentShape.shape[x][y] != 0:
                #check bounds
                if currentShape.x + x < 0 or currentShape.y + y < 0 or currentShape.x + x >= len(grid) or currentShape.y + y >= len(grid[0]):
                    return True
                if grid[currentShape.x + x][currentShape.y + y] != 0:
                    return True

#Returns next upcoming shape
def getNextShape():
    global ticker
    ticker = 0

    tempShape = Shape(upcoming[0])
    upcoming[0] = upcoming[1]
    upcoming[1] = upcoming[2]
    upcoming[2] = upcoming[3]
    upcoming[3] = randomShape()

    #move shape to center of grid
    tempShape.x = (int)(len(grid) / 2 - len(tempShape.shape) / 2)
    return tempShape

#Pick a random shape
def randomShape():
    return random.choice(list(shapes.keys()))

#Generate 4 upcoming blocks
def generateUpcoming():
    tempArr = []
    for i in range(4):
        tempArr.append(randomShape())
    return tempArr

#Clear rows that are matched
def clearRows():
    global grid
    global score
    global holdUsed
    global forceMove

    forceMove = 0
    holdUsed = False
    #List of rows that are full
    rows = []
    for y in reversed(range(len(grid[0]))):
        full = True
        for x in range(len(grid)):
            if grid[x][y] == 0:
                full = False
        if full:
            rows.append(y)

    #https://tetris.wiki/Scoring
    #TODO: implement T-spin and back to back difficult and combo

    multiplier = 0
    #Single
    if len(rows) == 1:
        multiplier = 100
    #Double
    elif len(rows) == 2:
        multiplier = 200
    #Triple
    elif len(rows) == 3:
        multiplier = 500
    #Tetris
    elif len(rows) == 4:
        multiplier = 800

    score += multiplier

    #delete rows to clear
    for row in rows:
        grid = np.delete(grid, row, 1)

    #add missing rows 
    tempRows = np.zeros((10, len(rows)))
    grid = np.hstack((tempRows, grid))

#Current player or Nnet lost
def handleLoss():    
    #update fitness of current Nnet
    suisei.setFitness(score)
    suisei.moveToNextNnet()
    resetGame()



def getNeuralInput():
    

    return inputs


def doBestMove(bestMove):
    # 0 : moveLeft
    # 1 : moveRight
    # 2 : rotateLeft
    # 3 : rotateRight
    # 4 : fastDrop
    # 5 : slowDrop
    # 6 : holdBlock
    # 7 : doNothing

    if bestMove == 0:
        #print('Move Left')
        moveLeft()
    elif bestMove == 1:
        #print('Move Right')
        moveRight()
    elif bestMove == 2:
        #print('Rotate Left')
        rotateLeft()
    elif bestMove == 3:
        #print('Rotate Right')
        rotateRight()
    elif bestMove == 4:
        #print('Fast Drop')
        fastDrop()
    elif bestMove == 5:
        #print('Slow Drop')
        moveDown()
    elif bestMove == 6:
        #print('Hold Block')
        hold()
    else:
        return
        #print('Doing Nothing')

        



