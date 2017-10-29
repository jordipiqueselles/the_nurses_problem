import random as rnd
import itertools as ittl
from enum import Enum

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

# TODO This function is not finished
def generateFeasible(distrDemand):
    """
    It creates a feasible instance of the problem
    :param distrDemand: Probabilistic distribution of the demand
    :return: A dictionary containing the params of a feasible instance
    """
    minHours = 0
    maxHours = 0
    maxConsec = 0
    maxPresence = 0

    distrDemand = (int(rnd.gauss(10, 2)) for _ in ittl.count())
    demand = [distrDemand.__next__() for _ in range(hoursDay)]

    nurses = []


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

distrMinHours = (int(rnd.gauss(4, 1)) for _ in ittl.count())
distrMaxHours = (int(rnd.gauss(10, 1)) for _ in ittl.count())
distrMaxConsec = (int(rnd.gauss(6, 1)) for _ in ittl.count())
distrMaxPresence = (int(rnd.gauss(12, 1)) for _ in ittl.count())
distrDemand = (int(rnd.gauss(20, 5)) for _ in ittl.count())

params = generateRandom(distrDemand, distrMinHours, distrMaxHours, distrMaxConsec, distrMaxPresence)
writeParams(params, "firstGenerated")