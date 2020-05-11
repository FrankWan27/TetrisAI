from enum import Enum
import numpy as np
import pygame

DISPLAY_W = 800
DISPLAY_H = 800
FPS = 60
WIDTH = 20
HEIGHT = 20
MAXHP = 500
MUTATION_RATE = 0.05
POP_SIZE = 50
PARENT_SIZE = 10

shapes = {
    'I':[[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]],
    'J':[[2, 2, 0, 0], [0, 2, 0, 0], [0, 2 ,0, 0], [0, 0, 0, 0]],
    'L':[[0, 3, 0, 0], [0, 3, 0, 0], [3, 3, 0, 0], [0, 0, 0, 0]],
    'O':[[0, 0, 0, 0], [0, 4, 4, 0], [0, 4, 4, 0], [0, 0, 0, 0]],
    'S':[[0, 5, 0, 0], [5, 5, 0, 0], [5, 0, 0, 0], [0, 0, 0, 0]],
    'T':[[0, 6, 0, 0], [6, 6, 0, 0], [0, 6, 0, 0], [0, 0, 0, 0]],
    'Z':[[7, 0, 0, 0], [7, 7, 0, 0], [0, 7, 0, 0], [0, 0, 0, 0]],
}

colors = {
    1:'cyan',
    'I':'cyan',
    2:'blue',
    'J':'blue',
    3:'orange',
    'L':'orange',
    4:'yellow',
    'O':'yellow',
    5:'green',
    'S':'green',
    6:'purple',
    'T':'purple',
    7:'red',
    'Z':'red'
}

class Dir(Enum):
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    UP = (0, -1)
    DOWN = (0, 1)

#Stores input hidden and out nums
class Species(Enum):
	TETRIS = (223, 20, 8)
	SNAKE = (24, 20, 12, 4)

#Converts a 2D Array to a 1D list
def arrayToList(arr, result):
    for x in range(len(arr)):
        for y in range(len(arr[0])):
            result.append(arr[x][y])
    return result

#Converts a 2D Array to a 1D list, and converts anything > 0 to 1
def arrayToOnes(arr, result):
    for x in range(len(arr)):
        for y in range(len(arr[0])):
            if arr[x][y] > 0:
                result.append(1)
            else:
                result.append(0)
    return result

#Simply picks a value between the two parents for every weight v
def mixArrays(a1, a2):
    rows = a1.shape[0]
    cols = a1.shape[1]
    
    output = np.zeros((rows, cols))


    for x in range(rows):
        for y in range(cols):
                if np.random.random() < 0.5:
                    output[x][y] = a1[x][y]
                else:
                    output[x][y] = a2[x][y]


    return output

#Mutates an array randomly by resetting [mutateChance]% of the weights.
def mutateArray(a, mutateChance):
    rows = a.shape[0]
    cols = a.shape[1]


    for x in range(rows):
        for y in range(cols):            
            if np.random.random() < mutateChance:

                #a[x][y] += np.random.gaussian() * 2
                a[x][y] = np.random.uniform(-1, 1)
                if a[x][y] > 1:
                    a[x][y] = 1
                elif a[x][y] < -1:
                    a[x][y] = -1

    return a

def sigmoid(x):
	return 1.0 / (1.0 + np.exp(-x))

def relu(x):
    return np.maximum(0, x)

def addBias(a):
    rows = a.shape[0]
    cols = a.shape[1]

    output = np.zeros((rows + 1, 1))

    for x in range(rows):
        output[x][0] = a[x][0]

    output[rows][0] = 1

    return output

import matplotlib
   
import matplotlib.pyplot as plt
import matplotlib.backends.backend_agg as agg




def plot(Xdata, Ydata, Ydata2):
    matplotlib.use("Agg")
    fig = plt.figure(figsize=[12, 3])
    canvas = agg.FigureCanvasAgg(fig)

    plt.plot(Xdata, Ydata, label="Highest Score")
    plt.plot(Xdata, Ydata2, label="Average Score")
    plt.ylim(bottom=0)
    plt.xlim(left=0)
    plt.xlabel('Generation')
    plt.ylabel('Fitness Score')
    plt.legend()
    plt.tight_layout()

    canvas.draw()
    renderer = canvas.get_renderer()

    raw_data = renderer.tostring_rgb()
    size = canvas.get_width_height()
    image = pygame.image.fromstring(raw_data, size, "RGB")
    plt.close()

    return image

def arrayToString(a):
    rows = a.shape[0]
    cols = a.shape[1]

    output = ""

    for x in range(rows):
        for y in range(cols):
            output += str(a[x][y]) + "\n"

    return output


