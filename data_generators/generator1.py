import random as rnd
import itertools as ittl
import copy

hoursDay = 24

def getNursesHours(nurses):
    return [sum(nurse) for nurse in nurses]

def getDemand(nurses):
    return [sum(col) for col in zip(*nurses)]

def getPresenceHours(nurses):
    nursesWithoutBegin = [list(ittl.dropwhile(lambda x: x == 0, nurse)) for nurse in nurses]
    nursesWithoutBeginAndEnd = [list(ittl.dropwhile(lambda x: x == 0, reversed(nurse))) for nurse in nursesWithoutBegin]
    return [len(nurse) for nurse in nursesWithoutBeginAndEnd]

def getConsecHours(nurses):
    nursesConsec = []
    for nurse in nurses:
        auxNurse = nurse
        maxConsecHours = 0
        while len(auxNurse) > 0:
            auxNurse = list(ittl.dropwhile(lambda x: x == 0, auxNurse))
            consecHours = len(list(ittl.takewhile(lambda x: x == 1, auxNurse)))
            maxConsecHours = max(maxConsecHours, consecHours)
            auxNurse = list(ittl.dropwhile(lambda x: x == 1, auxNurse))
        nursesConsec.append(maxConsecHours)
    return nursesConsec

def getRestingHours(nurses):
    nursesResting = []
    for nurse in nurses:
        maxRestingHours = 0
        # eliminate begin and tail
        auxNurse = list(ittl.dropwhile(lambda x: x == 0, nurse))
        auxNurse = list(ittl.dropwhile(lambda x: x == 0, reversed(auxNurse)))
        while len(auxNurse) > 0:
            auxNurse = list(ittl.dropwhile(lambda x: x == 1, auxNurse))
            consecRestHours = len(list(ittl.takewhile(lambda x: x == 0, auxNurse)))
            maxRestingHours = max(maxRestingHours, consecRestHours)
            auxNurse = list(ittl.dropwhile(lambda x: x == 0, auxNurse))
        nursesResting.append(maxRestingHours)
    return nursesResting

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
        result = "INFEASIBLE"
    elif sum(demand) > nNurses * maxHours:
        result = "INFEASIBLE"
    else:
        result = "UNKNOWN"

    # We could call part of the body of the function generateFeasible in order to try to generate a nurses
    # matrix that represents a solution. If we can generete this matrix, then a solution must exists

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
    totalNurseHours = getNursesHours(nurses)
    constrMinMaxHours = all((minHours <= nHours and nHours <= maxHours for nHours in totalNurseHours))

    # check satified demand
    nNursesInHour = getDemand(nurses)
    constrDemand = all((dem <= nNurses for dem in nNursesInHour))

    # check maxPresence
    nursesMaxPresence = getPresenceHours(nurses)
    constrMaxPresence = all((maxPresence >= presence for presence in nursesMaxPresence))

    # check maxConsec
    consecHours = getConsecHours(nurses)
    constrMaxConsec = all((maxConsec >= nurseConsecHours for nurseConsecHours in consecHours))

    # check resting hours
    restingHours = getRestingHours(nurses)
    constrRestHours = all((1 >= restHours for restHours in restingHours))

    allconstraints = [constrMinMaxHours, constrDemand, constrMaxPresence, constrMaxConsec, constrRestHours]
    return (all(allconstraints), allconstraints)

# Checking functions
def checkAllOk():
    distrDemand = (int(rnd.gauss(20, 5)) for _ in ittl.count())
    for _ in range(100):
        (params, nurses) = generateFeasible1(distrDemand)
        correct = isAnswerCorrect(nurses, params)
        assert correct
        feasibility = analyseFeasability(params)
        assert feasibility != "INFEASIBLE"
        (params, nurses) = generateFeasible2(rnd.randint(10,100))
        correct = isAnswerCorrect(nurses, params)
        assert correct
        feasibility = analyseFeasability(params)
        assert feasibility != "INFEASIBLE"

distrMinHours = (int(rnd.gauss(4, 1)) for _ in ittl.count())
distrMaxHours = (int(rnd.gauss(10, 1)) for _ in ittl.count())
distrMaxConsec = (int(rnd.gauss(6, 1)) for _ in ittl.count())
distrMaxPresence = (int(rnd.gauss(12, 1)) for _ in ittl.count())
distrDemand = (int(rnd.gauss(20, 5)) for _ in ittl.count())

# checkAllOk()

# params = generateRandom(distrDemand, distrMinHours, distrMaxHours, distrMaxConsec, distrMaxPresence)
# (params, nurses) = generateFeasible1(distrDemand)
(params, nurses) = generateFeasible2(20)
print(isAnswerCorrect(nurses, params))
writeParams(params, "firstGenerated.dat")
print(params)
print(nurses)