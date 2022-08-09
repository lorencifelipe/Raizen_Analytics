from problem import *
from math import inf

# Toggle the comment between lines 5 and 6 to "exhaustion test" or K limited solutions
#K = inf
K = 5

def main():
    file = "data.csv"
    problem = Problem(file)
    problem.createVars()
    problem.createModel()
    while problem.getSolutionCounter() < K:
        problem.callSolver()
        if problem.status() == "Optimal":
            check = problem.checkSolution()
            if check != True:
                print(check)
                break
            problem.incrementSolutionCounter()
            problem.writeSolution()
            problem.addCut()
        else:
            break


main()
