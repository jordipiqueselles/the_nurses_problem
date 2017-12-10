import itertools as ittl

def getNursesHours(nurses):
    """
    Get the amount of hours each nurse works
    :param nurses: A matrix. The cell (i, j) is 1 if nurse "i" works at time "j"
    :return: A list. The ith position have the number of hours the ith nurse works
    """
    return [sum(nurse) for nurse in nurses]


def getOffer(nurses):
    """
    Get the number of nurses that work at each hours
    :param nurses: A matrix. The cell (i, j) is 1 if nurse "i" works at time "j"
    :return: A list. The ith position have the number of nurses that work in the ith hour
    """
    return [sum(col) for col in zip(*nurses)]


def getPresenceHours(nurses):
    """
    For each nurse, gets the number of hours she is in the hospital
    :param nurses: A matrix. The cell (i, j) is 1 if nurse "i" works at time "j"
    :return: A list. The ith position have the number of hours the ith nurse spends at the hospital
    """
    nursesWithoutBegin = [list(ittl.dropwhile(lambda x: x == 0, nurse)) for nurse in nurses]
    nursesWithoutBeginAndEnd = [list(ittl.dropwhile(lambda x: x == 0, reversed(nurse))) for nurse in nursesWithoutBegin]
    return [len(nurse) for nurse in nursesWithoutBeginAndEnd]


def getConsecHours(nurses):
    """
    For each nurse, gets the maximum number of consecutive hours she works
    :param nurses: A matrix. The cell (i, j) is 1 if nurse "i" works at time "j"
    :return: A list. The ith position have the maximum number of consecutive hours the ith nurse works
    """
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
    """
    For each nurse, gets the maximum number of resting hours
    :param nurses: A matrix. The cell (i, j) is 1 if nurse "i" works at time "j"
    :return: A list. The ith position have the maximum number of resting hours for the ith nurse
    """
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


def analyseFeasability(params):
    """
    This function tries to determine if an instance of the problem is feasible or not
    :param params: The params of the instance of the problem
    :return: FEASIBLE if it is feasible, INFEASIBLE if it is unfeasible or UNKNOWN if it is not possible to determine
    it at a glance
    """
    minHours = params["minHours"]
    maxHours = params["maxHours"]
    maxConsec = params["maxConsec"]
    maxPresence = params["maxPresence"]
    demand = params["demand"]
    nNurses = params["nNurses"]

    if maxHours == 0 or maxHours < minHours or maxConsec == 0 or maxPresence == 0 or maxPresence < minHours:
        result = "INFEASIBLE"
    elif sum(demand) > nNurses * maxHours:
        result = "INFEASIBLE"
    else:
        result = "UNKNOWN"

    # We could call part of the body of the function generateFeasible in order to try to generate a nurses
    # matrix that represents a solution. If we can generete this matrix, then a solution must exists

    return result


def isFeasibleGeneratorOk(nurses, params):
    """
    Checks if a feasible generator gives a correct instance
    :param nurses: A matrix. The cell (i, j) is 1 if nurse "i" works at time "j"
    :param params: Parameters of the problem
    :return: True if it is correct, otherwise False
    """
    satConstr = answerSatisfiesConstr(nurses, params)
    feasibility = analyseFeasability(params)
    return satConstr and feasibility != "INFEASIBLE"


def answerSatisfiesConstr(nurses, params):
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

    # check we've used less than the maximum number of nurses
    constrNNurses = len(nurses) <= nNurses

    # drop the nurses that don't work
    nurses = list(filter(lambda nurse: sum(nurse) > 0, nurses))

    # check minHours and maxHours
    totalNurseHours = getNursesHours(nurses)
    constrMinMaxHours = all((minHours <= nHours <= maxHours for nHours in totalNurseHours))

    # check satisfied demand
    nNursesInHour = getOffer(nurses)
    constrDemand = all((dem <= nur for (nur, dem) in zip(nNursesInHour, demand)))

    # check maxPresence
    nursesMaxPresence = getPresenceHours(nurses)
    constrMaxPresence = all((maxPresence >= presence for presence in nursesMaxPresence))

    # check maxConsec
    consecHours = getConsecHours(nurses)
    constrMaxConsec = all((maxConsec >= nurseConsecHours for nurseConsecHours in consecHours))

    # check resting hours
    restingHours = getRestingHours(nurses)
    constrRestHours = all((1 >= restHours for restHours in restingHours))

    allconstraints = [constrNNurses, constrMinMaxHours, constrDemand,
                      constrMaxPresence, constrMaxConsec, constrRestHours]
    return all(allconstraints), allconstraints
