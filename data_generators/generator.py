import random as rnd
import copy
from otherScripts.checkingFunctions import *


def generateFeasible1(distrDemand, distrMaxHours, distrMaxConsec, distrMaxPresence, hoursDay):
    """
    It creates a feasible instance of the problem given a distribution of the demand
    :param distrDemand: Probabilistic distribution of the demand
    :param distrMaxHours: Probabilistic distribution of maxHours
    :param distrMaxConsec: Probabilistic distribution of maxConsec
    :param distrMaxPresence: Probabilistic distribution of maxPresence
    :param hoursDay: Number of hours in a day
    :return: A dictionary containing the params of a feasible instance and the matrix of a possible solution
    """
    maxHours = distrMaxHours.__next__()
    maxConsec = distrMaxConsec.__next__()
    maxPresence = distrMaxPresence.__next__()
    demand = [distrDemand.__next__() for _ in range(hoursDay)]

    nurses = []
    auxDemand = copy.copy(demand)
    while sum(auxDemand) > 0:
        nurse = []
        workedHours = 0
        consecHours = 0
        presenceHours = 0
        restHours = 0
        for h in range(hoursDay):
            if consecHours == maxConsec:
                nurse.append(0)
                consecHours = 0
                presenceHours += 1
                restHours = 1

            elif restHours == 1 or auxDemand[h] > 0:
                nurse.append(1)
                auxDemand[h] = max(0, auxDemand[h] - 1)
                restHours = 0
                workedHours += 1
                presenceHours += 1
                consecHours += 1

            elif workedHours > 0:
                nurse.append(0)
                consecHours = 0
                presenceHours += 1
                restHours = 1

            else:
                nurse.append(0)

            if workedHours == maxHours or presenceHours == maxPresence:
                nurse += [0] * (hoursDay - len(nurse))
                break
        nurses.append(nurse)

    minHours = min((sum(nurse) for nurse in nurses))
    nNurses = len(nurses)
    params = {"minHours": minHours, "maxHours": maxHours, "maxConsec": maxConsec, "maxPresence": maxPresence,
              "demand": demand, "nNurses": nNurses, "hoursDay": hoursDay}
    return params, nurses


def generateFeasible2(distrNNurses, hoursDay):
    """
    It creates a feasible instance for the problem given a number of nurses
    :param distrNNurses: Distribution of the number of nurses
    :param hoursDay: Number of hours in a day
    :return: The params of the problem and a solution for these params
    """
    nNurses = distrNNurses.__next__()
    nurses = []
    for _ in range(nNurses):
        m = rnd.randint(6, 18)
        start = min(max(0, int(rnd.gauss(m-5, 4))), hoursDay - 1)
        end = min(max(start+1, int(rnd.gauss(m+5, 4))), hoursDay)
        nurse = [0] * start + [1] * (end - start) + [0] * (hoursDay - end)
        restingHour = rnd.randint(start, end-1)
        nurse[restingHour] = 0
        if sum(nurse) == 0:
            nurse[restingHour] = 1
        nurses.append(nurse)

    params = {}
    params["hoursDay"] = hoursDay
    params["minHours"] = min(getNursesHours(nurses))
    params["maxHours"] = max(getNursesHours(nurses))
    params["maxConsec"] = max(getConsecHours(nurses))
    params["maxPresence"] = max(getPresenceHours(nurses))
    params["demand"] = getOffer(nurses)
    params["nNurses"] = nNurses

    return params, nurses


def generateRandom(distrDemand, distrMinHours, distrMaxHours, distrMaxConsec, distrMaxPresence, hoursDay):
    """
    It creates a random (feasible or unfeasible) instance of the problem
    All the distributions passed as a parameter must suppport the __next__() method
    :param distrDemand: Probabilistic distribution of the demand
    :param distrMinHours: Probabilistic distribution of minHours
    :param distrMaxHours: Probabilistic distribution of maxHours
    :param distrMaxConsec: Probabilistic distribution of maxConsec
    :param distrMaxPresence: Probabilistic distribution of maxPresence
    :param hoursDay: Number of hours in a day
    :return: A dictionary containing the params of an instance
    """
    minHours = max(0, distrMinHours.__next__())
    maxHours = max(0, distrMaxHours.__next__())
    maxConsec = max(0, distrMaxConsec.__next__())
    maxPresence = max(0, distrMaxPresence.__next__())
    demand = [distrDemand.__next__() for _ in range(hoursDay)]
    maxDemand = max(demand)
    nNurses = maxDemand + int(maxDemand/100 + 1) - rnd.randint(0, int(maxDemand/100 + 1))

    return {"hoursDay": hoursDay, "minHours": minHours, "maxHours": maxHours, "maxConsec": maxConsec,
            "maxPresence": maxPresence, "demand": demand, "nNurses": nNurses}


def writeParams(params, feasibility, file, cost=-1):
    """
    Writes an instance of the problem in a file
    :param params: Params containing the instance of the problem
    :param feasibility: If it is known that exists a feasible solution for the params
    :param file: File used to write the result
    """
    with open(file, 'w') as f:
        print("// " + feasibility, file=f)
        if cost > 0:
            print("// " + "COST " + str(cost), file=f)
        for key in sorted(params.keys(), reverse=True):
            print(key + "=" + str(params[key]).replace(",", "") + ";", file=f)
