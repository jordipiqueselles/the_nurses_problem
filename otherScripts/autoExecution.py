import os
import time
import subprocess
import math
from otherScripts.checkingFunctions import *
from metaheuristicas import grasp, graspNurses


class bcolors:
    """
    Class to write in colors to the print output
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def getParams(fileDat):
    """
    Exctracts the params from a .dat file and builds a dictionary
    :param fileDat: .dat file
    :return: A dictionary of the used params and the cost and if it is feasible (writen in comments in the .dat file)
    """
    with open(fileDat, mode='r') as f:
        d = {"solution": "UNKNOWN", "cost": math.inf}
        for line in f:
            line = line.replace("\n", "")
            if "=" in line:
                ll = line.split("=")
                name = ll[0]
                if "[" in ll[1]:
                    value = [int(number) for number in ll[1][1:-2].split(" ")]
                else:
                    value = int(ll[1][:-1])
                d[name] = value
            elif "INFEASIBLE" in line:
                d["solution"] = "INFEASIBLE"
            elif "FEASIBLE" in line:
                d["solution"] = "FEASIBLE"
            elif "COST" in line:
                d["cost"] = int(line.split()[-1])
    return d


def getSolution(strSolution):
    """
    From the output string of the oplrun.exe, it extracts the solution (if exists)
    :param strSolution: Output of the oplrun.exe
    :return: A matrix. The cell (i, j) is 1 if nurse "i" works at time "j"
    """
    if "no solution" in strSolution:
        return []
    else:
        ll = strSolution.split()
        index = ll.index("OBJECTIVE:") + 2
        retVal = []
        while ll[index] != "<<<":
            retVal.append([int(number) for number in ll[index]])
            index += 1
        return retVal


def executeOpl(pathToDat, solverParams):
    try:
        result = subprocess.check_output(pathToOPL + " " + pathToMod + " " + pathToDat, shell=True)
    except subprocess.CalledProcessError:
        # no solution
        return -1, []

    result = result.decode("utf-8")
    nurses = getSolution(result)
    cost = sum(sum(nurse) > 0 for nurse in nurses)
    return cost, nurses


def executeGrasp(pathToDat, solverParams):
    params = getParams(pathToDat)
    problem = graspNurses.graspNurses(params['demand'], params['minHours'], params['maxHours'], params['maxConsec'],
                                      params['maxPresence'])
    numIter = solverParams['numIter']
    alfa = solverParams['alfa']
    parallel = solverParams['parallel']
    if parallel:
        (cost, sol) = grasp.parallelGrasp(problem, numIter, alfa)
    else:
        (cost, sol) = grasp.grasp(problem, numIter, alfa)

    if cost <= params['nNurses']:
        return cost, sol
    else:
        return -1, []


def executeBrkga(pathToDat, solverParams):
    pass

def executeSolver(datFolder, solver, solverParams):
    """
    Executes all the files in the datFolder and prints the time consumed, the cost and checks several constraints in
    order to be sure the opl program works correctly
    :param datFolder: Folder with the .dat files
    """
    listDat = list(filter(lambda f: len(f) > 5 and f[-4:] == ".dat", os.listdir(datFolder)))
    for (i, file) in enumerate(listDat[:]):
        print(bcolors.BOLD + str(i+1) + "/" + str(len(listDat)) + bcolors.ENDC)
        print(bcolors.BOLD + "Executing", file, bcolors.ENDC)
        pathToDat = datFolder + file

        t = time.time()
        (cost, sol) = solver(pathToDat, solverParams)
        t = time.time() - t
        print("Time:", round(t, 2), "s")

        params = getParams(pathToDat)
        # no solution
        if cost == -1:
            print(bcolors.UNDERLINE + "no solution" + bcolors.ENDC)
            shouldBeInfeasible = params["solution"] != "FEASIBLE"
            print("should be infeasible:", shouldBeInfeasible)
            if shouldBeInfeasible:
                print(bcolors.OKGREEN + "OK" + bcolors.ENDC)
            else:
                print(bcolors.FAIL + "FAIL" + bcolors.ENDC)

        # solution feasible
        else:
            satConstr = answerSatisfiesConstr(sol, params)
            print(bcolors.UNDERLINE + "solution found" + bcolors.ENDC)
            print("cost:", cost)
            costOk = cost <= params["cost"]
            print("cost ok:", costOk)
            print("constrains satisfied:", satConstr[1])
            shouldBeFeasible = params["solution"] != "INFEASIBLE"
            print("should be feasible:", shouldBeFeasible)
            if costOk and satConstr[0] and shouldBeFeasible:
                print(bcolors.OKGREEN + "OK" + bcolors.ENDC)
            else:
                print(bcolors.FAIL + "FAIL" + bcolors.ENDC)
            # print(result)
        print()


if __name__ == '__main__':
    # PATHS
    pathToOPL = '"C:\Program Files\IBM\ILOG\CPLEX_Studio1271\opl\\bin\\x64_win64\oplrun.exe"'
    pathToOps = "../opl_project/opl_project.ops"
    pathToMod = "../opl_project/proves4.mod"

    manuallyGeneratedData = "../data_generators/manuallyGeneratedData/"
    autoGeneratedData = "../data_generators/autoGeneratedData/"
    graspParams = {'numIter': 50, 'alfa': 0.1, 'parallel': True}
    executeSolver(autoGeneratedData, executeGrasp, graspParams)

    # import os
    # os.system("shutdown.exe /h")
