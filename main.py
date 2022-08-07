from problem import *


def main():
    file = "data.csv"
    problem = Problem(file)
    problem.createVars()
    problem.createModel()

    while True:  # or it. limit
        problem.callSolver()
        if problem.status() == "Optimal":
            problem.incrementSolutionCounter()
            problem.writeSolution()
            problem.addCut()
        else:
            break


main()
