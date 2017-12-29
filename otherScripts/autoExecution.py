import os
import sys
import time
import subprocess
import math
from otherScripts.checkingFunctions import *
from metaheuristicas import grasp, graspNurses, brkga
# from otherScripts.utils import eprint


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

    # result = []
    try:
        # result = subprocess.check_output(pathToOPL + " " + pathToMod + " " + pathToDat, shell=True)
        # print(pathToOPL + ' -p "." ' + configName)
        result = subprocess.check_output(pathToOPL + ' -v -p "." ' + configName, shell=True)
        # process = subprocess.Popen(pathToOPL + ' -v -p "." ' + configName, shell=True,
        #                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #
        # while True:
        #     nextline = process.stdout.readline()
        #     result.append(nextline)
        #     if process.poll() is not None:
        #         break
        #     print(nextline.decode("utf-8"), end='')
        #
        # output = process.communicate()[0]
        # exitCode = process.returncode

    except subprocess.CalledProcessError:
        # no solution
        return -1, []

    # result = ''.join(result)
    result = result.decode("utf-8")
    # print(result)
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

    (cost, sol) = grasp.parallelGrasp(problem, numIter, alfa, nThreads, maxTime, maxItWithoutImpr)

    if cost <= params['nNurses']:
        return cost, sol
    else:
        return -1, []


def executeBrkga(pathToDat, maxTime, solverParams):
    params = getParams(pathToDat)
    chrLen = brkga.getChrLength(params)
    numIndividuals = solverParams['numIndividuals']
    maxGenerations = solverParams['maxGenerations']
    eliteProp = solverParams['eliteProp']
    mutantsProp = solverParams['mutantsProp']
    inheritanceProp = solverParams['inheritanceProb']
    maxItWithoutImpr = solverParams['maxItWithoutImpr']

    solver = brkga.Brkga(brkga.decode)
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
    for (i, file) in enumerate(listDat[13:]):
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
        print()

        if writeResults:
            resultsFile.write(file + ", " + str(cost) + ", " + str(t) + "\n")

    if writeResults:
        resultsFile.close()


if __name__ == '__main__':
    # Parameters for the solvers
    oplParams = {'pathToOPL': '"C:\Program Files\IBM\ILOG\CPLEX_Studio1271\opl\\bin\\x64_win64\oplrun.exe"',
                 'pathToMod': "../opl_project/nurses4.mod",
                 'maxMemory': 12000}

    graspParams = {'numIter': 200000,
                   'alfa': 0.1,
                   'nThreads': 8,
                   'maxItWithoutImpr': 300000}

    brkgaParams = {'numIndividuals': 200,
                   'maxGenerations': 200,
                   'eliteProp': 0.1,
                   'mutantsProp': 0.2,
                   'inheritanceProb': 0.7,
                   'maxItWithoutImpr': 100000}

    # Data folders
    manuallyGeneratedData = "../data_generators/manuallyGeneratedData/"
    autoGeneratedData = "../data_generators/autoGeneratedData/"
    benchmark = "C:\\Users\pique\Downloads\\benchmark\\"

    # Max time (seconds) for solving one instance
    maxTime = 5*60

    # verbose
    sys.argv += ['-v']
    if '-v' not in sys.argv:
        nullFile = open('nul', 'w')
        sys.stderr = nullFile

    # write results in a file
    sys.argv += ['-w']
    if '-w' in sys.argv:
        fileName = "./results" + str(maxTime) + "s_"
    else:
        fileName = None

    # executeSolver(autoGeneratedData, executeGrasp, maxTime, graspParams, fileName)
    executeSolver(autoGeneratedData, executeBrkga, maxTime, brkgaParams, fileName)
    # executeSolver(autoGeneratedData, executeOpl, maxTime, oplParams, fileName)

    # maxTime = 10*60
    # fileName = "./results" + str(maxTime) + "s_"
    # executeSolver(autoGeneratedData, executeBrkga, maxTime, brkgaParams, fileName)

    # os.system("shutdown.exe /h")
