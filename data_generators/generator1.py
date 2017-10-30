import random as rnd
import itertools as ittl
from enum import Enum
import copy

"""
"""
class Result(Enum):
    """
    Class used to indicate if an instance of the problem is feasible, infeasible or cannot be deduced at a glance
    """
    FEASIBLE = 0
    INFEASIBLE = 1
    UNKNOWN = 2

hoursDay = 24

def generateFeasible(distrDemand):
    """
    It creates a feasible instance of the problem
    :param distrDemand: Probabilistic distribution of the demand
    :return: A dictionary containing the params of a feasible instance and the matrix of a possible solution
    """
    maxHours = 10
    maxConsec = 6
    maxPresence = 12
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

            elif restHours == 1 or demand[h] > 0:
                nurse.append(1)
                auxDemand[h] = max(0, auxDemand[h] - 1)
                restHours = 0
                workedHours += 1
                presenceHours += 1
                consecHours += 1

            else:
                nurse.append(0)

            if workedHours == maxHours or presenceHours == maxPresence:
                nurse += [0] * (hoursDay - len(nurse))
                break
        nurses.append(nurse)

    minHours = min((sum(nurse) for nurse in nurses))
    nNurses = len(nurses)
    params = {"minHours": minHours, "maxHours": maxHours, "maxConsec": maxConsec, "maxPresence": maxPresence,
            "demand": demand, "nNurses": nNurses}
    return (params, nurses)


def generateRandom(distrDemand, distrMinHours, distrMaxHours, distrMaxConsec, distrMaxPresence):
    """
    It creates a random (feasible or unfeasible) instance of the problem
    All the distributions passed as a parameter must suppport the __next__() method
    :param distrDemand: Probabilistic distribution of the demand
    :param distrMinHours: Probabilistic distribution of minHours
    :param distrMaxHours: Probabilistic distribution of maxHours
    :param distrMaxConsec: Probabilistic distribution of maxConsec
    :param distrMaxPresence: Probabilistic distribution of maxPresence
    :return: A dictionary containing the params of an instance
    """
    minHours = max(0, distrMinHours.__next__())
    maxHours = max(0, distrMaxHours.__next__())
    maxConsec = max(0, distrMaxConsec.__next__())
    maxPresence = max(0, distrMaxPresence.__next__())
    # distrDemand = (int(rnd.gauss(10, 2)) for _ in ittl.count())
    demand = [distrDemand.__next__() for _ in range(hoursDay)]
    nNurses = max(demand) + 2 - rnd.randint(0, 2)

    return {"minHours": minHours, "maxHours": maxHours, "maxConsec": maxConsec, "maxPresence": maxPresence,
            "demand": demand, "nNurses": nNurses}

def analyseFeasability(params):
    """
    This function tries to determine if an instance of the problem is feasible or not
    :param params: The params of the instance of the problem
    :return: FEASIBLE if it is feasible, INFEASIBLE if it is unfeasible or UNKNOWN if it is not possible to determine it at a glance
    """
    minHours = params["minHours"]
    maxHours = params["maxHours"]
    maxConsec = params["maxConsec"]
    maxPresence = params["maxPresence"]
    demand = params["demand"]
    nNurses = params["nNurses"]

    if maxHours == 0 or maxHours < minHours or maxConsec == 0 or maxPresence == 0:
        result = Result.INFEASIBLE
    elif sum(demand) > nNurses * maxHours:
        result = Result.INFEASIBLE
    else:
        result = Result.UNKNOWN

    return result

def writeParams(params, file):
    """
    Writes an instance of the problem in a file
    :param params: Params containing the instance of the problem
    :param file: File used to write the result
    """
    with open(file, 'w') as f:
        for key in params:
            print(key + "=" + str(params[key]).replace(",", "") + ";", file=f)

def isAnswerCorrect(nurses, params):
    """
    Checks if the answer satisfies all the constrains
    :param nurses: Matrix (nRows = nNurses, nCols = nHours) representing the answer to the problem
    :param params: Params of an instance of the problem
    :return: True if the answer satisfy all the constraints
    """
    minHours = params["minHours"]
    maxHours = params["maxHours"]
    maxConsec = params["maxConsec"]
    maxPresence = params["maxPresence"]
    demand = params["demand"]
    nNurses = params["nNurses"]

    # check we have exactly nNurses
    constrNNurses = nNurses == len(nurses)

    # drop the nurses that don't work
    nurses = list(filter(lambda nurse: sum(nurse) > 0, nurses))

    # check minHours and maxHours
    totalNurseHours = [sum(nurse) for nurse in nurses]
    constrMinMaxHours = all((minHours <= nHours and nHours <= maxHours for nHours in totalNurseHours))

    # check satified demand
    nNursesInHour = [sum(col) for col in zip(*nurses)]
    constrDemand = all((dem <= nNurses for (dem, nNurses) in zip(demand, nNursesInHour)))

    # check maxPresence
    nursesWithoutBegin = [ittl.dropwhile(lambda x: x == 0, nurse) for nurse in nurses]
    nursesWithoutBeginAndEnd = [ittl.dropwhile(lambda x: x == 0, reversed(nurse)) for nurse in nursesWithoutBegin]
    constrMaxPresence = all((maxPresence >= len(nurse) for nurse in nursesWithoutBeginAndEnd))

    # check maxConsec
    constrMaxConsec = True
    for nurse in nurses:
        auxNurse = nurse
        while len(auxNurse) > 0:
            auxNurse = ittl.dropwhile(lambda x: x == 0, auxNurse)
            consecHours = len(list(ittl.takewhile(lambda x: x == 1, auxNurse)))
            auxNurse = ittl.dropwhile(lambda x: x == 1, auxNurse)
            constrMaxConsec = constrMaxConsec and (consecHours <= maxConsec)

    # check resting hours
    constrRestHours = True
    for nurse in nurses:
        # eliminate begin and tail
        auxNurse = list(ittl.dropwhile(lambda x: x == 0, nurse))
        auxNurse = list(ittl.dropwhile(lambda x: x == 0, reversed(auxNurse)))
        while len(auxNurse) > 0:
            auxNurse = ittl.dropwhile(lambda x: x == 1, auxNurse)
            consecRestHours = len(list(ittl.takewhile(lambda x: x == 0, auxNurse)))
            auxNurse = ittl.dropwhile(lambda x: x == 0, auxNurse)
            constrRestHours = constrRestHours and (consecRestHours <= 1)



distrMinHours = (int(rnd.gauss(4, 1)) for _ in ittl.count())
distrMaxHours = (int(rnd.gauss(10, 1)) for _ in ittl.count())
distrMaxConsec = (int(rnd.gauss(6, 1)) for _ in ittl.count())
distrMaxPresence = (int(rnd.gauss(12, 1)) for _ in ittl.count())
distrDemand = (int(rnd.gauss(20, 5)) for _ in ittl.count())

params = generateRandom(distrDemand, distrMinHours, distrMaxHours, distrMaxConsec, distrMaxPresence)
writeParams(params, "firstGenerated.dat")