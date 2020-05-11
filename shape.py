from defs import *
import copy 
class Shape:
    x = 0
    y = 0
    shape = []
    letter = ''
    rotation = 0

    def __init__(self, shapeLetter='S'):
        self.letter = shapeLetter
        self.shape = copy.deepcopy(shapes[shapeLetter])



