# Import libraries
import os
import pandas as pd
from math import inf
from pulp import *

# Class Problem
class Problem:

    # Indexer method
    def idx(self, a, b):
        return(str(a)+"_"+str(b))

    # Indexer method
    def idxc(self, a, b, c):
        return(str(a)+"_"+str(b)+"_"+str(c))

    # Method to load file
    def loadFile(self, file):
        return pd.read_csv(file, encoding="latin1")

    # Method to load containers
    def loadContainers(self):
        return list(self.df["container"].unique())

    # Method to load boxes
    def loadBoxes(self):
        boxes = []
        for a in self.indexedBoxes:
            for b in self.indexedBoxes[a]:
                boxes.append(self.idx(a, b))
        return boxes
    
    # Method to load cylinders
    def loadCylinders(self):
        cylinders = []
        for b in self.indexedCylinders:
            for c in self.indexedCylinders[b]:
                cylinders.append(self.idx(b, c))
        return cylinders

    # Method to load indexed boxes 
    def loadIndexedBoxes(self):
        indexedBoxes = {}
        for a in self.containers:
            indexedBoxes[a] = list(self.df.query(
                "container == @a")["box"].unique())
        return indexedBoxes

    # Method to load indexed Cylinders
    def loadIndexedCylinders(self):
        indexedCylinders = {}
        for a in self.indexedBoxes:
            for b in self.indexedBoxes[a]:
                indexedCylinders[self.idx(a, b)] = list(
                    self.df.query("container == @a and box == @b")["cylinder"].unique())
        return indexedCylinders

    # Method to load weight/volume
    def loadInfo(self, column):
        info = {}
        for a in self.indexedBoxes:
            for b in self.indexedBoxes[a]:
                cylindersIndexes = list(self.df.query(
                    "container == @a and box == @b")["cylinder"].unique())
                for c in cylindersIndexes:
                    info[self.idxc(a, b, c)] = round(float(self.df.query("container == @a and box == @b and cylinder == @c")[column]), 2)
        return info

    # Method to create problem variables
    def createVars(self):
        for a in self.containers:
            name = "x_"+a
            self.x[a] = LpVariable(name, cat=LpBinary)
        for b in self.boxes:
            name = "y_" + b
            self.y[b] = LpVariable(name, cat=LpBinary)
        for c in self.cylinders:
            name = "z_" + c
            self.z[c] = LpVariable(name, cat=LpBinary)
    
    # Method to create the model itself
    def createModel(self):
        #Constraint 1
        self.prob += lpSum([self.x[a] for a in self.containers]) == 35
        #Constraint 2
        self.prob += lpSum([self.cylindersVolume[c]*self.z[c] for c in self.cylinders]) == 5163.69
        #Constraint 3
        self.prob += lpSum([self.cylindersWeight[c]*self.z[c] for c in self.cylinders]) == 18844
        #Constraint 4
        for a in self.containers:
            self.prob += lpSum([self.y[self.idx(a,b)] for b in self.indexedBoxes[a]]) <= self.x[a]*len(self.indexedBoxes[a]) 
        #Constraint 5
        for a in self.containers:
            self.prob += lpSum([self.y[self.idx(a,b)] for b in self.indexedBoxes[a]]) >= self.x[a]
        #Constraint 6
        for b in self.boxes:
            self.prob += lpSum([self.z[self.idx(b,c)] for c in self.indexedCylinders[b]]) == self.y[b]

    # Method to solve the problem
    def callSolver(self):
        self.prob.solve()

    # Method to check the problem status
    def status(self):
        return LpStatus[self.prob.status]

    # Method to write the problem solution
    def writeSolution(self):
        dir = os.getcwd()
        if not os.path.exists(dir+"/results"):
            os.makedirs("results")
        os.chdir(dir+"/results")
        solution = open(str(self.solutionCounter)+".txt","w")
        for a in self.x:
            solution.write("x_"+str(a)+": "+str(value(self.x[a]))+"\n")
        for b in self.y:
            solution.write("y_"+str(b)+": "+str(value(self.y[b]))+"\n")
        for c in self.z:
            solution.write("z_"+str(c)+": "+str(value(self.z[c]))+"\n")
        solution.close()
        os.chdir(dir)

    # Method to count the number of z variables in the solution
    def countZ(self):
        counter = 0
        for c in self.z:
            if value(self.z[c]) == 1: counter+=1
        return counter

    # Method to add a cut in the model
    def addCut(self):
        self.prob += lpSum([self.z[c] for c in self.cylinders if value(self.z[c]) == 1]) <= self.countZ() - 1 #or zCount

    # Method to check the solution delivered by the model
    def checkSolution(self):
        approved = True

        # Check number of containers
        numberContainers = 0
        for a in self.containers:
            if value(self.x[a]) == 1:
                numberContainers+=1
        if numberContainers != 35: 
            approved = "WARNING: the solution does not have 35 containers."   

        # Check Volume/Weight
        totalVolume, totalWeight = 0, 0
        for c in self.cylinders:
            if value(self.z[c]) == 1:
                totalVolume += self.cylindersVolume[c]
                totalWeight += self.cylindersWeight[c]
        if round(totalVolume,2) != 5163.69:
            approved = "WARNING: the sum of cylinders' volumes is different from 5163.69."
        if totalWeight != 18844:
            approved = "WARNING: the sum of cylinder' weight is different from 18844." 
        
        # Check if (for each selected container) -> (at least one selected box)
        # Check if (for each not select container) -> (there are no selected boxes)
        for a in self.containers:
            if value(self.x[a]) == 1:
                for b in self.indexedBoxes[a]:
                    if value(self.y[self.idx(a,b)]) == 1:
                        break
                else:
                    approved = "WARNING: problem in boxes' selection."
            else:
                for b in self.indexedBoxes[a]:
                    if value(self.y[self.idx(a,b)]) == 1:
                        approved = "WARNING: problem in boxes' selection."

        # Check if (for each select box) -> (there is exactly one selected cylinder from this box)
        # Check if (for each not selected box) ->  (there can be no cylinders selected)
        for b in self.boxes:
            if value(self.y[b]) == 1:
                cylinderCounter = 0
                for c in self.indexedCylinders[b]:
                    if value(self.z[self.idx(b,c)]) == 1:
                        cylinderCounter +=1
                if cylinderCounter!=1:
                    approved = "WARNING: problem in cylinders' selection."
            else:
                cylinderCounter = 0
                for c in self.indexedCylinders[b]:
                    if value(self.z[self.idx(b,c)]) == 1:
                        cylinderCounter+=1
                if cylinderCounter > 0:
                    approved = "WARNING: problem in cylinders' selection"

        return approved

    # Method to increment solutionCounter 
    def incrementSolutionCounter(self):
        self.solutionCounter+=1

    # Method to get solutionCounter
    def getSolutionCounter(self):
        return self.solutionCounter

    # Class Constructor Method
    def __init__(self, file):
        self.solutionCounter = 0
        self.df = self.loadFile(file)
        self.containers = self.loadContainers()
        self.indexedBoxes = self.loadIndexedBoxes()
        self.boxes = self.loadBoxes()
        self.indexedCylinders = self.loadIndexedCylinders()
        self.cylinders = self.loadCylinders()
        self.cylindersWeight = self.loadInfo("cylinderWeight")
        self.cylindersVolume = self.loadInfo("cylinderVolume")
        self.prob = LpProblem("Cylinders_Problem")
        self.x, self.y, self.z = {}, {}, {}