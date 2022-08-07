import pandas as pd
from pulp import *

# Class Problem


class Problem:

    # Indexer method -> Make pvt
    def idx(self, a, b):
        return(str(a)+"_"+str(b))

    def idx(self, a, b, c):
        return(str(a)+"_"+str(b)+"_"+str(c))

    # Method to load file -> Make pvt
    def loadFile(self, file):
        return pd.read_csv(file, encoding="latin1")

    # Method to load containeres -> Make pvt
    def loadContainers(self):
        return list(self.df["container"].unique())

    # Method to load boxes -> Make pvt
    def loadBoxes(self):
        boxes = []
        for a in self.indexed_boxes:
            for b in self.indexed_boxes[a]:
                boxes.append(self.idx(a, b))
        return boxes

    # Method to load indexed boxes -> Make pvt
    def loadIndexedBoxes(self):
        indexedBoxes = {}
        for a in self.containeres:
            indexedBoxes[a] = list(self.df.query(
                "container == @a")["box"].unique())
        return indexedBoxes

    # Method to load indexed Cylinders -> Make pvt
    def loadIndexedCylinders(self):
        indexedCylinders = {}
        for a in self.indexedBoxes:
            for b in self.indexedBoxes[a]:
                indexedCylinders[self.idx(a, b)] = list(
                    self.df.query("container == @a and box == @b")["cylinder"].unique())
        return indexedCylinders

    # Method to load cylinders -> Make pvt
    def loadCylinders(self):
        cylinders = []
        for b in self.indexedCylinders:
            for c in self.indexedCylinders[b]:
                cylinders.append(self.idx(b, c))
        return cylinders

    # Method to load weight/volume -> Make pvt
    def loadInfo(self, column):
        info = {}
        for a in self.indexedBoxes:
            for b in self.indexedBoxes[a]:
                cylindersIndexes = list(self.df.query(
                    "container == @a and box == @b")["cylinder"].unique())
                for c in cylindersIndexes:
                    info[self.idx(a, b, c)] = round(float(self.df.query(
                        "container == @a and box == @b and cylinder == @c")[column]), 2)
        return info


    ## Public ##

    #Create Variables
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

    # Constructor
    def __init__(self, file):
        self.df = self.loadFile(file)
        self.containers = self.loadContainers()
        self.indexedBoxes = self.loadIndexedBoxes()
        self.boxes = self.loadBoxes()
        self.indexedCylinders = self.loadIndexedCylinders()
        self.cylinders = self.loadCylinders()
        self.cylindersWeight = self.loadInfo("cylinderWeight")
        self.cylindersVolume = self.loadInfo("cylindersVolume")
        self.prob = LpProblem("Cylinders_Problem")
        self.x, self.y, self.z = {}, {}, {}
        