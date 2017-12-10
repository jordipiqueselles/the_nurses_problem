import copy
import random as rnd
import math
import multiprocessing as mp
from functools import partial
from otherScripts.checkingFunctions import *

hoursDay = 24


def recursiveGenerateAllNurses(nurse, maxConsec, initHour, nHours):
    constrMaxConsec = getConsecHours([nurse])[0] <= maxConsec

    if not constrMaxConsec:
        return []

    elif nHours == 0:
        return [nurse]

    else:
        nurses = []
        for hour in range(initHour, min(initHour + 2, len(nurse) - nHours + 1)):
            auxNurse = copy.copy(nurse)
            auxNurse[hour] = 1
            nurses += recursiveGenerateAllNurses(auxNurse, maxConsec, hour + 1, nHours - 1)
        return nurses


def generateAllNurses(params):
    minHours = params["minHours"]
    maxHours = params["maxHours"]
    maxConsec = params['maxConsec']
    maxPresence = params["maxPresence"]

    nurses = []
    for nHours in range(minHours, maxHours+1):
        # print("Generating with nHours ->", nHours)
        nurse = [1] + [0] * (maxPresence - 1)
        nurses += recursiveGenerateAllNurses(nurse, maxConsec, 1, nHours - 1)

    # print("Total nurses generated:", len(nurses))
    # drop the 0s at the end
    nurses = [list(ittl.dropwhile(lambda x: x == 0, reversed(nurse))) for nurse in nurses]
    return nurses


def checkConstraints(nurse, params):  # except minHours
    maxHours = params["maxHours"]
    maxConsec = params["maxConsec"]
    maxPresence = params["maxPresence"]

    # check maxHours
    constrMaxHours = getNursesHours([nurse])[0] <= maxHours
    # check maxPresence
    constrMaxPresence = getPresenceHours([nurse])[0] <= maxPresence
    # check maxConsec
    constrMaxConsec = getConsecHours([nurse])[0] <= maxConsec
    # check resting hours
    constrRestHours = getRestingHours([nurse])[0] <= 1

    return constrMaxHours and constrMaxPresence and constrMaxConsec and constrRestHours


def greedyCostNurse(feasibleNurses, demand, nElems=100, nPos=5):
    listGreedyCost = []
    for _ in range(nElems):
        idx = rnd.randint(0, len(feasibleNurses) - 1)
        auxNurse = feasibleNurses[idx]
        for _ in range(nPos):
            pos = rnd.randint(0, len(demand) - len(auxNurse))
            # Create nurse. It's a deep copy of the nurse selected from feasibleNurses
            nurse = [0] * pos + auxNurse + [0] * (len(demand) - pos - len(auxNurse))
            greedyCost = sum((demand[i] * (1 - nurse[i]) for i in range(len(demand))))
            listGreedyCost.append((greedyCost, nurse))

    return listGreedyCost


def constructNurses(params, alfa=0.1):
    feasibleNurses = params["feasibleNurses"]
    demand = params["demand"]
    nurses = []
    auxDemand = copy.copy(demand)

    # We don't have a solution until all the demand is satisfied
    while sum(auxDemand) > 0:
        listGreedyCost = greedyCostNurse(feasibleNurses, auxDemand)
        minCost = min(listGreedyCost)[0]
        maxCost = max(listGreedyCost)[0]
        RCL = [elem[1] for elem in listGreedyCost if elem[0] <= minCost + alfa*(maxCost - minCost)]
        randomElem = RCL[rnd.randint(0, len(RCL)-1)]
        nurses.append(randomElem)
        auxDemand = [max(0, auxDemand[i] - randomElem[i]) for i in range(len(auxDemand))]

    nNurses = len(nurses)
    return nurses, nNurses


def getListFreeNurses(nurses, params):
    freeNurses = [set() for _ in range(len(nurses[0]))]
    for (i, nurse) in enumerate(nurses):
        for (h, work) in enumerate(nurse):
            if not work:
                nurse[h] = 1
                if checkConstraints(nurse, params):
                    freeNurses[h].add(i)
                nurse[h] = 0
    return freeNurses


def localSearchNurses(nurses, params):
    demand = params["demand"]
    offerNurses = getOffer(nurses)
    extraNurses = [offerNurses[i] - demand[i] for i in range(len(demand))]
    freeNurses = getListFreeNurses(nurses, params)

    # try to eliminate every nurse
    for (i, nurse) in enumerate(nurses):
        if nurse is None:
            continue

        dictSubstitutes = {}
        canEliminate = True

        # for all hours from a nurse
        for (h, work) in enumerate(nurse):
            if work == 0 or extraNurses[h] > 0:
                continue

            # try to assign the hours to other nurses
            for idNurse in freeNurses[h]:
                otherNurse = nurses[idNurse]
                otherNurse[h] = 1
                if checkConstraints(otherNurse, params):
                    dictSubstitutes[h] = idNurse
                    break
                else:
                    otherNurse[h] = 0

            # we couldn't find a substitute for the j-th hour
            if h not in dictSubstitutes:
                canEliminate = False
                break

        if canEliminate:
            # update free nurses
            for (hour, idNurse) in dictSubstitutes.items():
                freeNurses[hour].remove(idNurse)
            for setNurses in freeNurses:
                if i in setNurses:
                    setNurses.remove(i)

            # update extraNurses
            for (h, work) in enumerate(nurse):
                # if the hour has been eliminated, not swapped with another nurse
                if h not in dictSubstitutes:
                    extraNurses[h] = extraNurses[h] - work
            # "delete" nurse
            nurses[i] = None

        else:
            # reset values for modified nurses
            for (hour, idNurse) in dictSubstitutes.items():
                nurses[idNurse][hour] = 0

    nurses = list(filter(lambda nurse: nurse is not None, nurses))
    return nurses, len(nurses)


def grasp(params, construct, localSearch, maxIter=10, alfa=0.1):
    """
    General GRASP algorithm
    :param params: Dictionary (instance for the problem)
    :param construct: Function to construct the initial solution
    :param localSearch: Function for local search
    :param maxIter: Maximum number of iterations
    :return: The best solution and the best cost
    """
    bestSol = None
    bestCost = math.inf
    for i in range(maxIter):
        # print("Iteration", i)
        (sol, cost) = construct(params, alfa)
        (sol, cost) = localSearch(sol, params)
        if cost < bestCost:
            bestSol = sol
            bestCost = cost
    return bestCost, bestSol


def parallelGrasp(params, construct, localSearch, maxIter=10, alfa=0.1, nThreads=mp.cpu_count()):
    with mp.Pool(nThreads) as pool:
        # def auxGrasp(i):
        #     return grasp(params, construct, localSearch, 1 + maxIter // nThreads, alfa)
        # listResults = pool.map(auxGrasp, range(nThreads))
        listResults = pool.map(partial(grasp, construct=construct, localSearch=localSearch,
                                       maxIter=1 + maxIter//nThreads), [params]*nThreads)
        bestResult = min(listResults)
        return bestResult


if __name__ == '__main__':
    from data_generators.generator import generateFeasible2, generateFeasible1
    from otherScripts.autoExecution import getParams

    # random generators for the different variables of an instance of the problem
    distrMinHours = (int(rnd.gauss(4, 1)) for _ in ittl.count())
    distrMaxHours = (int(rnd.gauss(10, 1)) for _ in ittl.count())
    distrMaxConsec = (int(rnd.gauss(6, 1)) for _ in ittl.count())
    distrMaxPresence = (int(rnd.gauss(12, 1)) for _ in ittl.count())
    distrDemand = (int(rnd.gauss(150, 20)) for _ in ittl.count())

    # (params, sol) = generateFeasible2(200)
    # (params, oldSol) = generateFeasible1(distrDemand)
    # print("Cost generator ->", len(oldSol))
    # (sol, cost) = constructNurses(params, 0.1)
    # print(params["demand"])
    # print(getOffer(sol))
    # print(answerSatisfiesConstr(sol, params))
    # print("Cost constructor ->", cost)
    # (sol, cost) = localSearchNurses(sol, params)
    # print(answerSatisfiesConstr(sol, params))
    # print("Cost local search ->", cost)
    # exit(0)

    for _ in range(20):
        # (params, oldSol) = generateFeasible1(distrDemand)
        # print("Cost generator ->", len(oldSol))
        params = getParams('../data_generators/autoGeneratedData/feasible2_3.dat')

        (sol, cost) = constructNurses(params, 0.1)
        ok = answerSatisfiesConstr(sol, params)
        print(ok)
        assert ok[0]
        print("Cost constructor ->", cost)

        (sol, cost) = localSearchNurses(sol, params)
        ok = answerSatisfiesConstr(sol, params)
        print(ok)
        assert ok[0]
        print("Cost local search ->", cost)

        print()

    # for _ in range(20):
    #     (params, oldSol) = generateFeasible1(distrDemand)
    #     print(params)
    #     oldCost = len(oldSol)
    #     print(oldCost)
    #
    #     (sol, cost) = localSearchNurses(copy.copy(oldSol), params)
    #     print(sol)
    #     print(cost)
    #     sat = answerSatisfiesConstr(sol, params)
    #     print(sat)
    #     assert all(sat[1][1:])
    #
    #     # (sol, cost) = localSearchNurse(copy.copy(oldSol), params)
    #     # print(sol)
    #     # print(cost)
    #     # sat = answerSatisfiesConstr(sol, params)
    #     # print(sat)
    #     # assert all(sat[1][1:])
    #
    #     print()
