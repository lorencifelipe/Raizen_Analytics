import pandas as pd
from pulp import *

# PENDENCIAS
# Melhorar leitura
# Melhorar checker
# privts
# checar padrões
# Comment


def checkSolution():
    ok = True

    # check number of containeres
    numberX = 0
    for a in containeres:
        if value(x[a]) == 1:
            numberX += 1
    if numberX != 35:
        ok = False

    ## ARREDONDAMENTO
    # # check volume
    totalVolume = 0
    for c in cylinders:
        if value(z[c]) == 1:
            totalVolume += cylinders_volume[c]
    if totalVolume != 5163.69: #roundhere
        ok = False

    # check weight
    totalWeight = 0
    for c in cylinders:
        if value(z[c]) == 1:
            totalWeight += cylinders_weight[c]
    if totalWeight != 18844:
        ok = False

    # Verificar se para cada container selecionado, há pelo menos uma caixa selecionada
    # E para cada container NÃO selecionado, não podem haver caixas selecionadas
    for a in containeres:
        if value(x[a]) == 1:
            for b in indexed_boxes[a]:
                if value(y[a+"_"+b]) == 1:
                    break
            else:
                ok = False
        else:
            for b in indexed_boxes[a]:
                if value(y[a+"_"+b]) == 1:
                    ok = False
            # indexed_boxes

    # Verificar se para cada caixa selecionada, há EXATAMENTE 1 cilindro DESSA CAIXA selecionado
    # E para cada caixa não selecionada, não podem haver cilindros selecionados
    for b in boxes:
        if value(y[b]) == 1:
            cylinderCounter = 0
            for c in indexed_cylinders[b]:
                if value(z[b+"_"+str(c)])==1:
                    cylinderCounter+=1
            if cylinderCounter != 1:
                ok = False
        else:
            cylinderCounter = 0
            for c in indexed_cylinders[b]:
                if value(z[b+"_"+str(c)])==1:
                    cylinderCounter+=1
            if cylinderCounter > 0:
                ok = False


    return ok

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
    prob += lpSum([y[a+"_"+b] for b in indexed_boxes[a]]
                  ) <= x[a]*len(indexed_boxes[a])  # update form

for a in containeres:
    prob += lpSum([y[a+"_"+b] for b in indexed_boxes[a]]) >= x[a]

for b in boxes:
    prob += y[b] == lpSum([z[b+"_"+str(c)] for c in indexed_cylinders[b]])

# STOP HERE


# Extra constraints

# Para cada container, se

solution_counter = 0


def countZ(z):
    c = 0
    for a in z:
        if(value(z[a]) == 1):
            c += 1
    return c


while True:
    prob.solve()
    if LpStatus[prob.status] == "Optimal":
        for a in x:
            print(a + ": " + str(value(x[a])))

        for a in y:
            print(a + ": " + str(value(y[a])))

        for a in z:
            print(a + ": " + str(value(z[a])))

        z_count = countZ(z)
        # cut opt. sol.
        #prob += lpSum([z[c] for c in cylinders if value(z[c]) == 1]) <= 34
        prob += lpSum([z[c] for c in cylinders if value(z[c]) == 1]) <= z_count - 1

        solution_counter += 1
        print("Solution counter: " + str(solution_counter))
    else:
        break
    ok = checkSolution()
    print(ok)


print("Total solutions: " + str(solution_counter))
# #call solver
# prob.solve()

# for a in x:
#     print(a + ": " + str(value(x[a])))

# for a in y:
#     print(a + ": " + str(value(y[a])))

# for a in z:
#     print(a + ": " + str(value(z[a])))
