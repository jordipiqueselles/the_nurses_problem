import random as rnd
import itertools as ittl
import copy
from otherScripts.checkingFunctions import *

hoursDay = 24

def generateFeasible1(distrDemand):
    """
    It creates a feasible instance of the problem given a distribution of the demand
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
            "demand": demand, "nNurses": nNurses}
    return (params, nurses)


def generateFeasible2(nNurses):
    """
    It creates a feasible instance for the problem given a number of nurses
    :param nNurses: The number of nurses
    :return: The params of the problem and a solution for these params
    """
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
    params["minHours"] = min(getNursesHours(nurses))
    params["maxHours"] = max(getNursesHours(nurses))
    params["maxConsec"] = max(getConsecHours(nurses))
    params["maxPresence"] = max(getPresenceHours(nurses))
    params["demand"] = getDemand(nurses)
    params["nNurses"] = nNurses

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


def writeParams(params, feasibility, file, cost=-1):
    """
    Writes an instance of the problem in a file
    :param params: Params containing the instance of the problem
    :param file: File used to write the result
    """
    with open(file, 'w') as f:
        print("// " + feasibility, file=f)
        if cost > 0:
            print("// " + "COST " + str(cost), file=f)
        for key in params:
            print(key + "=" + str(params[key]).replace(",", "") + ";", file=f)


# def checkAllOk():
#     distrDemand = (int(rnd.gauss(20, 5)) for _ in ittl.count())
#     for _ in range(100):
#         (params, nurses) = generateFeasible1(distrDemand)
#         correct = answerSatisfiesConstr(nurses, params)
#         assert correct
#         feasibility = analyseFeasability(params)
#         assert feasibility != "INFEASIBLE"
#         (params, nurses) = generateFeasible2(rnd.randint(10, 100))
#         correct = answerSatisfiesConstr(nurses, params)
#         assert correct
#         feasibility = analyseFeasability(params)
#         assert feasibility != "INFEASIBLE"

distrMinHours = (int(rnd.gauss(4, 1)) for _ in ittl.count())
distrMaxHours = (int(rnd.gauss(10, 1)) for _ in ittl.count())
distrMaxConsec = (int(rnd.gauss(6, 1)) for _ in ittl.count())
distrMaxPresence = (int(rnd.gauss(12, 1)) for _ in ittl.count())
distrDemand = (int(rnd.gauss(20, 5)) for _ in ittl.count())

nInstFeasible = 5
listFeasibleGenerators = [generateFeasible1, generateFeasible2]
for i in range(nInstFeasible*2):
    if i < nInstFeasible:
        name = "feasible1_" + str(i+1) + ".dat"
        (params, nurses) = generateFeasible1(distrDemand)
    else:
        name = "feasible2_" + str(i-nInstFeasible+1) + ".dat"
        (params, nurses) = generateFeasible2(rnd.randint(15,25))
    assert isFeasibleGeneratorOk(nurses, params)
    cost = sum(sum(nurse) > 0 for nurse in nurses)
    writeParams(params, "FEASIBLE", "autoGeneratedData/" + name, cost)