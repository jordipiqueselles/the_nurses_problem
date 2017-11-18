import copy
import random as rnd
import math
from otherScripts.checkingFunctions import *

hoursDay = 24

def greedyCostNurse(nurse, demand, params):
    minHours = params["minHours"]
    maxHours = params["maxHours"]
    maxConsec = params["maxConsec"]
    maxPresence = params["maxPresence"]

    greedyCost = []

    for (i, hour) in enumerate(nurse):
        if hour == 0:
            nurse[i] = 1

            # check minHours and maxHours
            constrMinMaxHours = getNursesHours([nurse])[0] <= maxHours
            # check maxPresence
            constrMaxPresence = getPresenceHours([nurse])[0] <= maxPresence
            # check maxConsec
            constrMaxConsec = getConsecHours([nurse])[0] <= maxConsec
            # check resting hours
            constrRestHours = getRestingHours([nurse])[0] <= 1

            if constrMinMaxHours and constrMaxPresence and constrMaxConsec and constrRestHours:
                greedyCost[i] = 1 / (demand + 0.00001) # avoid dividing by 0

            nurse[i] = 0

        else:
            greedyCost.append(math.inf)

    # TODO Constraint minHours


def constructNurse(params, alfa=0.1):
    demand = params["demand"]

    nurses = []
    auxDemand = copy.copy(demand)
    while sum(auxDemand) > 0:
        nurse = [0*hoursDay]
        greedyCost = greedyCostNurse(nurse, demand, params)
        minCost = min(greedyCost)
        maxCost = max(greedyCost)
        RCL = [elem[0] for elem in enumerate(greedyCost) if elem[1] <= minCost + alfa*(maxCost - minCost)]
        randomElem = RCL[rnd.randint(0, len(RCL)-1)]
        nurses[randomElem] = 1
        auxDemand[randomElem] = max(0, auxDemand[randomElem] - 1)

    nNurses = len(nurses)
    return nurses, nNurses


def localSearchNurse(x):
    # TODO Eliminate one nurse and assing her hours to the others
    pass


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
    return (bestSol, bestCost)