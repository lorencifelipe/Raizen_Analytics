import pandas as pd
from pulp import *
# Leitura

file_name = "data.csv"

df = pd.read_csv(file_name, encoding="latin1")

containeres = list(df["container"].unique())

indexed_boxes = {}

for a in containeres:
    indexed_boxes[a] = list(df.query("container == @a")["box"].unique())

boxes = []

for a in indexed_boxes:
    for b in indexed_boxes[a]:
        boxes.append(a+"_"+b)

indexed_cylinders = {}

for a in indexed_boxes:
    for b in indexed_boxes[a]:
        indexed_cylinders[a+"_"+b] = list(
            df.query("container == @a and box == @b")["cylinder"].unique())

cylinders = []

for b in indexed_cylinders:
    for c in indexed_cylinders[b]:
        cylinders.append(b+"_"+str(c))

cylinders_weight = {}
cylinders_volume = {}

for a in indexed_boxes:
    for b in indexed_boxes[a]:
        cylinders_indexes = list(
            df.query("container == @a and box == @b")["cylinder"].unique())
        for c in cylinders_indexes:

            cylinders_weight[a+"_"+b+"_"+str(c)] = float(
                df.query("container == @a and box == @b and cylinder == @c")["cylinderWeight"])
            cylinders_volume[a+"_"+b+"_"+str(c)] = float(
                df.query("container == @a and box == @b and cylinder == @c")["cylinderVolume"])


# Modelo
prob = LpProblem("Raizen")

# Adding variables

x = {}
y = {}
z = {}

for a in containeres:
    name = "x_"+a
    x[a] = LpVariable(name, cat=LpBinary)

for b in boxes:
    name = "y_" + b
    y[b] = LpVariable(name, cat=LpBinary)

for c in cylinders:
    name = "z_" + c
    z[c] = LpVariable(name, cat=LpBinary)

# #Add constraints

prob += lpSum([x[a] for a in containeres]) == 35

prob += lpSum([cylinders_volume[c]*z[c] for c in cylinders]) == 5163.69

prob += lpSum([cylinders_weight[c]*z[c] for c in cylinders]) == 18844

for a in containeres:
    prob += lpSum([y[a+"_"+b] for b in indexed_boxes[a]]) <= x[a]*len(indexed_boxes)

for a in containeres: 
    prob += lpSum([y[a+"_"+b] for b in indexed_boxes[a]]) >= x[a]

for b in boxes:
    prob += y[b] == lpSum([z[b+"_"+str(c)] for c in indexed_cylinders[b]])

#call solver
prob.solve()

for a in x:
    print(a + ": " + str(value(x[a])))

for a in y:
    print(a + ": " + str(value(y[a])))

for a in z:
    print(a + ": " + str(value(z[a])))