import os
import time
import subprocess
import math
from otherScripts.checkingFunctions import *
from metaheuristicas import generalGrasp, graspNurses, generalBrkga, decoderNurses


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
            line = line.replace(" = ", "=")
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


def executeOpl(pathToDat, maxTime, solverParams):
    pathToOPL = solverParams['pathToOPL']
    pathToMod = solverParams['pathToMod']
    configName = "ConfigForPython"

    with open(".oplproject", 'w') as f:
        f.write("""<?xml version="1.0" encoding="ASCII"?><project>
<version>1.0</version>
    <configs>
		<config default="true" name=""" + '"' + configName + '"' + """ category="opl">
			<ref name=""" + '"' + pathToMod + '"' + """ type="model">
            </ref>
            <ref name="./opl_project.ops" type="setting">
            </ref>
            <ref name=""" + '"' + pathToDat + '"' + """ type="data">
            </ref>
        </config>
    </configs>
</project>""")

    maxMemory = solverParams['maxMemory']

    with open("opl_project.ops", 'w') as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<settings version="2">
  <category name="cplex">
    <setting name="tilim" value=""" + '"' + str(maxTime) + '"' + """/>
    <setting name="workmem" value=""" + '"' + str(maxMemory) + '"' + """/>
  </category>
</settings>""")

    try:
        result = subprocess.check_output(pathToOPL + ' -v -p "." ' + configName, shell=True)
    except subprocess.CalledProcessError:
        # no solution
        return -1, []

    result = result.decode("utf-8")
    nurses = getSolution(result)
    cost = sum(sum(nurse) > 0 for nurse in nurses)
    return cost, nurses


def executeGrasp(pathToDat, maxTime, solverParams):
    params = getParams(pathToDat)
    problem = graspNurses.GraspNurses(params['demand'], params['minHours'], params['maxHours'], params['maxConsec'],
                                      params['maxPresence'])
    numIter = solverParams['numIter']
    alfa = solverParams['alfa']
    nThreads = solverParams['nThreads']
    maxItWithoutImpr = solverParams['maxItWithoutImpr']

    (cost, sol) = generalGrasp.parallelGrasp(problem, numIter, alfa, nThreads, maxTime, maxItWithoutImpr)

    if cost <= params['nNurses']:
        return cost, sol
    else:
        return -1, []


def executeBrkga(pathToDat, maxTime, solverParams):
    params = getParams(pathToDat)
    chrLen = decoderNurses.getChrLength(params)
    numIndividuals = solverParams['numIndividuals']
    maxGenerations = solverParams['maxGenerations']
    eliteProp = solverParams['eliteProp']
    mutantsProp = solverParams['mutantsProp']
    inheritanceProp = solverParams['inheritanceProb']
    maxItWithoutImpr = solverParams['maxItWithoutImpr']

    solver = generalBrkga.Brkga(decoderNurses.decode)
    (cost, solution) = solver.run(params, chrLen, numIndividuals, maxGenerations, eliteProp,
                                  mutantsProp, inheritanceProp, maxTime, maxItWithoutImpr)

    if answerSatisfiesConstr(solution, params)[0]:
        return cost, solution
    else:
        return -1, []


def executeSolver(datFolder, solver, maxTime, solverParams, fileName=None):
    """
    Executes all the files in the datFolder and prints the time consumed, the cost and checks several constraints in
    order to be sure the opl program works correctly
    :param datFolder: Folder with the .dat files
    :param solver:
    :param maxTime:
    :param solverParams:
    :param fileName:
    """
    writeResults = fileName is not None
    if writeResults:
        fileName = fileName + '_' + solver.__name__ + ".txt"
        resultsFile = open(fileName, 'w')
        resultsFile.write("dat_file, cost, time \n")

    listDat = list(filter(lambda f: len(f) > 5 and f[-4:] == ".dat", os.listdir(datFolder)))
    listDat.sort(key=lambda f: len(f))
    for (i, file) in enumerate(listDat[:]):
        print(bcolors.BOLD + str(i+1) + "/" + str(len(listDat)) + " (" + solver.__name__ + ")" + bcolors.ENDC)
        print(bcolors.BOLD + "Executing", file, bcolors.ENDC)
        pathToDat = datFolder + file

        t = time.time()
        (cost, sol) = solver(pathToDat, maxTime, solverParams)
        t = time.time() - t
        print("Time:", round(t, 2), "s")

        params = getParams(pathToDat)
        # no solution
        if cost == -1:
            print(bcolors.UNDERLINE + "no solution" + bcolors.ENDC)
            print("should be:", params["solution"])
            shouldBeInfeasible = params["solution"] != "FEASIBLE"
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
            print("should be:", params["solution"])
            shouldBeFeasible = params["solution"] != "INFEASIBLE"
            if costOk and satConstr[0] and shouldBeFeasible:
                print(bcolors.OKGREEN + "OK" + bcolors.ENDC)
            else:
                print(bcolors.FAIL + "FAIL" + bcolors.ENDC)
        print()

        if writeResults:
            resultsFile.write(file + ", " + str(cost) + ", " + str(t) + "\n")

    if writeResults:
        resultsFile.close()
