import copy
import random as rnd
import math
import multiprocessing as mp
from otherScripts.checkingFunctions import *

hoursDay = 24


def checkConstraints(nurse, params):  # except minHours
    minHours = params["minHours"]
    maxHours = params["maxHours"]
    maxConsec = params["maxConsec"]
    maxPresence = params["maxPresence"]

    # check minHours
    if getNursesHours([nurse])[0] >= minHours:
        constrMinHours = True
    else:
        constrMinHours = True

    # check maxHours
    constrMaxHours = getNursesHours([nurse])[0] <= maxHours
    # check maxPresence
    constrMaxPresence = getPresenceHours([nurse])[0] <= maxPresence
    # check maxConsec
    constrMaxConsec = getConsecHours([nurse])[0] <= maxConsec
    # check resting hours
    constrRestHours = getRestingHours([nurse])[0] <= 1

    return constrMaxHours and constrMaxPresence and constrMaxConsec and constrRestHours


def greedyCostNurse(nurse, demand, params):
    greedyCost = [math.inf] * hoursDay

    for (i, hour) in enumerate(nurse):
        if hour == 0:
            nurse[i] = 1
            ok = checkConstraints(nurse, params)
            if ok:
                greedyCost[i] = 1 / (demand[i] + 0.00001)  # avoid dividing by 0
            nurse[i] = 0

    return greedyCost


def constructNurses(params, alfa=0.1):
    demand = params["demand"]
    nurses = [[0] * hoursDay]
    auxDemand = copy.copy(demand)

    # We don't have a solution until all the demand is satisfied
    while sum(auxDemand) > 0:  # and nurses[-1] -> minHours
        greedyCost = greedyCostNurse(nurses[-1], auxDemand, params)
        if all((math.isinf(elem) for elem in greedyCost)):
            nurses.append([0] * hoursDay)
            continue

        minCost = min(greedyCost)
        maxCost = max(filter(lambda x: not math.isinf(x), greedyCost))
        RCL = [elem[0] for elem in enumerate(greedyCost) if elem[1] <= minCost + alfa*(maxCost - minCost)]
        randomElem = RCL[rnd.randint(0, len(RCL)-1)]
        nurses[-1][randomElem] = 1
        auxDemand[randomElem] = max(0, auxDemand[randomElem] - 1)

    nNurses = len(nurses)
    return nurses, nNurses


def localSearchNurse(nurses, params):
    demand = params["demand"]
    offerNurses = getOffer(nurses)
    extraNurses = [offerNurses[i] - demand[i] for i in range(len(demand))]

    canEliminateNurse = True
    while canEliminateNurse:

        # try to eliminate every nurse
        for (i, nurse) in enumerate(nurses):
            canEliminateNurse = True
            # make a copy of nurses without the selected nurse
            remainingNurses = nurses[:i] + nurses[i+1:]
            auxExtraNurses = copy.copy(extraNurses)

            # for all hours from a nurse
            for (j, h) in enumerate(nurse):
                if h == -1:
                    canEliminateNurse = False
                    break

                elif h == 1:
                    # if there's more nurses than needed we can eliminate the hour this nurse works
                    if auxExtraNurses[j] > 0:
                        auxExtraNurses[j] -= 1
                        continue

                    # try to assign this hour to any of the remaining nurses
                    canChangeHour = False
                    for (k, otherNurse) in enumerate(remainingNurses):
                        if otherNurse[j] == 0:
                            otherNurse[j] = 1
                            ok = checkConstraints(otherNurse, params)
                            if ok:
                                canChangeHour = True
                                break
                            else:
                                otherNurse[j] = 0

                    if not canChangeHour:
                        canEliminateNurse = False
                        break

            if canEliminateNurse:
                # nurses = remainingNurses
                for i in range(len(nurse)):
                    nurse[i] = -1
                extraNurses = auxExtraNurses
                break

            # move the hours this nurse works where the number of extra nurses is lower
            elif False:
                minExtraNurses = min(extraNurses)
                minIdx = extraNurses.index(minExtraNurses)

                if nurse[minIdx] == 0:
                    # nurse[minIdx] = 1
                    # ok = checkConstraints(nurse, params)
                    # if not ok:
                    #     nurse[minIdx] = 0

                    oldSum = sum(nurse)
                    # for all hours from a nurse
                    for (j, h) in enumerate(nurse):
                        if h == 1 and extraNurses[j] > 0:
                            nurse[j] = 0
                            nurse[minIdx] = 1
                            ok = checkConstraints(nurse, params)
                            if ok:
                                extraNurses[j] -= 1
                                extraNurses[minIdx] += 1
                            else:
                                nurse[j] = 1
                                nurse[minIdx] = 0

                    assert oldSum == sum(nurse)

    nurses = [nurse for nurse in nurses if sum(nurse) >= 0]
    return nurses, len(nurses)


def grasp(params, construct, localSearch, maxIter):
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
    for _ in range(maxIter):
        (sol, cost) = construct()
        (sol, cost) = localSearch(sol)
        if cost < bestCost:
            bestSol = sol
            bestCost = cost
    return bestCost, bestSol


def parallelGrasp(params, construct, localSearch, maxIter, nThreads=mp.cpu_count()):
    with mp.Pool(nThreads) as pool:
        listResults = pool.map(grasp(params, construct, localSearch, maxIter//nThreads), range(nThreads))
        bestResult = min(listResults)
        return bestResult


from data_generators.generator import generateFeasible2, generateFeasible1

# random generators for the different variables of an instance of the problem
distrMinHours = (int(rnd.gauss(4, 1)) for _ in ittl.count())
distrMaxHours = (int(rnd.gauss(10, 1)) for _ in ittl.count())
distrMaxConsec = (int(rnd.gauss(6, 1)) for _ in ittl.count())
distrMaxPresence = (int(rnd.gauss(12, 1)) for _ in ittl.count())
distrDemand = (int(rnd.gauss(150, 20)) for _ in ittl.count())

# (params, sol) = generateFeasible2(200)
# (sol, cost) = constructNurses(params, 0.1)
# print(params["demand"])
# print(getOffer(sol))
# print(answerSatisfiesConstr(sol, params))
# exit(0)

for _ in range(20):
    (params, sol) = generateFeasible1(distrDemand)
    print(params)
    print(len(sol))
    (sol, cost) = localSearchNurse(sol, params)
    print(sol)
    print(cost)
    sat = answerSatisfiesConstr(sol, params)
    print(sat)
    print()
    assert all(sat[1][1:])