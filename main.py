from problem import *

def main():
    file = "data.csv"
    problem = Problem(file)
    problem.createVars()
    problem.createModel()

    while True:  
        problem.callSolver()
        if problem.status() == "Optimal": # or it. limit 
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
