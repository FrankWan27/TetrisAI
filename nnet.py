import numpy as np
import pygame
from defs import *
import copy 



class Nnet:
    wInputToHidden = []

    wHiddenToHidden = []
    wHiddenToOutput = []

    #Fitness:Calculated by score/time
    fitness = -10000000

    def __init__(self, species, filename = None):
        self.numInputs = species.value[0]
        self.numHidden = species.value[1]
        self.numHidden2 = species.value[2]
        self.numOutputs = species.value[3]
        
        if(filename != None):
            self.loadBest(filename)
        else:
            self.initWeights()

    #Randomly generates a uniformly distributed weights matrix
    def initWeights(self, low = -1, high = 1):

        #includes bias

        self.wInputToHidden = np.random.uniform(low, high, size=(self.numHidden, self.numInputs + 1))
        self.wHiddenToHidden = np.random.uniform(low, high, size=(self.numHidden2, self.numHidden + 1))
        self.wHiddenToOutput = np.random.uniform(low, high, size=(self.numOutputs, self.numHidden2 + 1))  




        #self.wInputToHidden = 

        #self.wInputToHidden = np.array([
        #    [0.4, 0, 0, 0, -5, 0, 0, 0, 5, 0, 0, 0], 
        #    [0, 0.3, 0, 0, 0, -5, 0, 0, 0, 5, 0, 0], 
         #   [0, 0, 0.1, 0, 0, 0, -5, 0, 0, 0, 5, 0], 
        #    [0, 0, -0.2, 0.5, 0, 0, 0, -5, 0, 0, 0, 5]
         #   ])


    #Return outputs given an input 
    def getOutputs(self, inputList):

        inputs = addBias(np.array(inputList, ndmin=2).T)

        hiddenValues = addBias(relu(np.dot(self.wInputToHidden, inputs)))
        #print(inputs)
        #print(self.wInputToHidden)

        hiddenValues2 = addBias(relu(np.dot(self.wHiddenToHidden, hiddenValues)))



        outputs = sigmoid(np.dot(self.wHiddenToOutput, hiddenValues2))
        #outputs = sigmoid(np.dot(self.wManual, inputs)) 

        #print(outputs)
        
        return outputs

    def getHidden(self, inputList):
        inputs = addBias(np.array(inputList, ndmin=2).T)

        hiddenValues = sigmoid(np.dot(self.wInputToHidden, inputs))
        return hiddenValues
    
    def getHidden2(self, inputList):
        inputs = addBias(np.array(inputList, ndmin=2).T)

        hiddenValues = addBias(sigmoid(np.dot(self.wInputToHidden, inputs)))

        hiddenValues2 = sigmoid(np.dot(self.wHiddenToHidden, hiddenValues))

        return hiddenValues2

        
    def getOptimalOutput(self, inputList):
        output = self.getOutputs(inputList)

        #randomly choose tiebreaks
        return np.random.choice(np.flatnonzero(np.isclose(output, output.max())))


    def makeChild(self, mom, dad):
        self.wInputToHidden = mutateArray(mixArrays(mom.wInputToHidden, dad.wInputToHidden), MUTATION_RATE)
        self.wHiddenToHidden = mutateArray(mixArrays(mom.wHiddenToHidden, dad.wHiddenToHidden), MUTATION_RATE)
        self.wHiddenToOutput = mutateArray(mixArrays(mom.wHiddenToOutput, dad.wHiddenToOutput), MUTATION_RATE)

    def loadBest(self, filename):

        self.wInputToHidden = np.zeros((self.numHidden, self.numInputs + 1))
        self.wHiddenToHidden = np.zeros((self.numHidden2, self.numHidden + 1))
        self.wHiddenToOutput = np.zeros((self.numOutputs, self.numHidden2 + 1))  


        f = open(filename, "r")

        for x in range(self.wInputToHidden.shape[0]):
            for y in range(self.wInputToHidden.shape[1]):
                self.wInputToHidden [x][y] = float(f.readline())
        
        for x in range(self.wHiddenToHidden.shape[0]):
            for y in range(self.wHiddenToHidden.shape[1]):
                self.wHiddenToHidden[x][y] = float(f.readline())
        
        for x in range(self.wHiddenToOutput.shape[0]):
            for y in range(self.wHiddenToOutput.shape[1]):
                self.wHiddenToOutput[x][y] = float(f.readline())


class Nnets:
    #Constants
    popSize = POP_SIZE
    numParents = PARENT_SIZE

    #Trackers
    highscoreHistory = []
    generationHistory = []
    avgscoreHistory = []
    highscore = -1
    highestScore = -1
    highestGen = -1
    genAvg = -1
    genTotal = 0
    graph = None

    allTimeNnet = None



    def __init__(self, species):
        self.species = species
        self.nnets = []
        self.currentNnet = 0
        self.generation = 0

    def createPop(self, filename = None):
        for i in range(self.popSize):
            self.nnets.append(Nnet(self.species, filename))

    def moveToNextNnet(self):
        self.currentNnet += 1
        if(self.currentNnet >= self.popSize):
            self.evolve()

    def getBestMove(self, inputList):
        return self.nnets[self.currentNnet].getOptimalOutput(inputList)

    def setFitnessIndex(self, index, score):
        self.nnets[index].fitness = score
        #print(self.nnets[self.currentNnet].wInputToHidden)
        #print(self.nnets[self.currentNnet].wHiddenToOutput)

        
        #update highscores
        if score > self.highscore:
            self.highscore = score
            if self.highscore > self.highestScore:
                self.highestScore = score
                self.allTimeNnet = self.nnets[index]

        #update averages
        if index < PARENT_SIZE:
            self.genTotal += score
            self.genAvg = self.genTotal / (index + 1) 
        
    def setFitness(self, score):
        self.setFitnessIndex(self.currentNnet, score)
        

    def evolve(self):
        #get top 10 performers
        bestNnets = []

        #Keep top 10 performers
        for i in range(self.numParents):
            bestNnets.append(self.popBestNnet())

        childNnets = []
        #Rest of population will be children of top 10
        for i in range(self.popSize - self.numParents):
            mom = self.selectRandom(bestNnets)
            dad = self.selectRandom(bestNnets)
            childNnets.append(self.makeChild(mom, dad))


        #Rest of population will be modified versions of top 10
        #for i in range(self.popSize - self.numParents):
        #    mom = bestNnets[np.random.randint(self.numParents)]
        #    bestNnets.append(self.makeClone(mom))

        self.generationHistory.append(self.generation)
        self.highscoreHistory.append(self.highscore)
        self.avgscoreHistory.append(self.genAvg)
        self.generation += 1
        self.currentNnet = 0
        self.highscore = 0
        self.genTotal = 0
        self.nnets = bestNnets + childNnets
        self.graph = plot(self.generationHistory, self.highscoreHistory, self.avgscoreHistory)


    def makeChild(self, mom, dad):
        child = Nnet(self.species)
        child.makeChild(mom, dad)
        return child

    def selectRandom(self, nnets):
        fitnessSum = 0
        for i in range(len(nnets)):
            fitnessSum += nnets[i].fitness

        randFit = np.random.uniform(0, fitnessSum)

        runningSum = 0

        for i in range(len(nnets)):
            runningSum += nnets[i].fitness
            if runningSum > randFit:
                return nnets[i]

    def popBestNnet(self):
        bestFit = -1
        bestIndex = 0
        for i in range(len(self.nnets)):
            if self.nnets[i].fitness > bestFit:
                bestIndex = i
                bestFit = self.nnets[i].fitness

        return self.nnets.pop(bestIndex)

    def writeBest(self, filename):
        if self.allTimeNnet is not None:
            f = open(filename, "w")
            wIH = arrayToString(self.allTimeNnet.wInputToHidden)
            wHH = arrayToString(self.allTimeNnet.wHiddenToHidden)
            wHO = arrayToString(self.allTimeNnet.wHiddenToOutput)
            f.write(wIH + wHH + wHO)
            f.close()