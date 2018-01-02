import math
import itertools as ittls
from otherScripts.utils import eprint
from otherScripts.checkingFunctions import getOffer

def getChrLength(params):
    """
    Gets the length of the chromosome for an instance of the nurses problem
    :param params: Parameters defining an instance of the nurses problem
    :return: The length of the chromosome
    """
    maxHours = params["maxHours"]
    maxConsec = params["maxConsec"]
    maxPresence = params["maxPresence"]

    # Sometimes it's impossible to work exactly maxHours
    maxHours = int(min(maxHours, maxPresence - math.ceil(maxPresence / maxConsec) + 1))
    # Max number of groups of consecutive working hours
    maxNumGroupConsecH = min(params['maxPresence'] - maxHours + 1, maxHours * 2 - 1)
    # Length of an encoded nurse
    lengthEncodedNurse = maxNumGroupConsecH + 2
    return params['nNurses'] * lengthEncodedNurse


def createProportionDemand3(demand, maxPresence, maxHours, lastInitHour):
    l = len(demand)
    maxPresence = min(maxPresence, l)
    r = maxHours / maxPresence
    auxDemand = demand + []
    prob = [0] * l

    for i in range(min(l//2, lastInitHour)):
        prob[i] = max(0.1, auxDemand[i])
        prob[l-i-1] = max(0.1, auxDemand[l-i-1])
        for j in range(i+1, min(i+maxPresence, l)):
            auxDemand[j] -= r * prob[i]
            auxDemand[l-j-1] -= r * prob[l-i-1]

    # print([round(p, 2) for p in prob])
    sumIni = sum(prob[:(l + 1) // 2])
    sumFi = sum(prob[(l + 1) // 2:])
    for i in range(1, (l + 1) // 2):
        prob[i] += prob[i - 1]
        prob[l - i - 1] += prob[l - i]
    firstHalf = [elem / sumIni for elem in prob[:(l + 1) // 2]]
    secondHalf = [elem / sumFi for elem in reversed(prob[(l + 1) // 2:])]

    # print([round(p, 2) for p in firstHalf])
    # print([round(p, 2) for p in secondHalf])
    return sumIni / (sumIni + sumFi), firstHalf, secondHalf


def decode(population, params):
    """
    Deocder for the nurses optimization problem
    :param population: [{'chr': chromosome, ...}, {...}, ...]
    :param params: Dictionary with hoursDay, minHours, maxHours, maxConsec, maxPresence, demand and nNurses
    :return: [{'chr': chromosome, 'solution': solution, 'fitness': fitness}, ...]
    """
    hoursDay = params['hoursDay']
    # minHours = params["minHours"]
    maxHours = params["maxHours"]
    maxConsec = params["maxConsec"]
    maxPresence = params["maxPresence"]
    demand = params["demand"]
    nNurses = params['nNurses']

    # Sometimes it's impossible to work exactly maxHours
    maxHours = int(min(maxHours, maxPresence - math.ceil(maxPresence / maxConsec) + 1))
    # Max number of groups of consecutive working hours
    maxNumGroupConsecH = min(maxPresence - maxHours + 1, maxHours * 2 - 1)
    # Max length of an encoded nurse
    maxLenEncNurse = maxNumGroupConsecH + 2
    # Last hour when the working day of a nurse can start
    # lastInitHour = hoursDay - maxPresence
    lastInitHour = min((hoursDay + 1) // 2, hoursDay - maxHours - math.ceil(maxHours / maxConsec) + 1 + 1)

    lenWorkingDay = min(maxPresence, maxHours * 2 - 1)
    if 'propHalf' not in params or 'firstHalf' not in params or 'secondHalf' not in params:
        (propHalf, firstHalf, secondHalf) = createProportionDemand3(demand, lenWorkingDay, maxHours, lastInitHour)
        params['propHalf'] = propHalf
        params['firstHalf'] = firstHalf
        params['secondHalf'] = secondHalf
    else:
        propHalf = params['propHalf']
        firstHalf = params['firstHalf']
        secondHalf = params['secondHalf']

    # totalTime = 0
    listSolutions = []
    populationChr = (ind['chr'] for ind in population)
    for encodedSetNurses in populationChr:
        nurses = []
        nWorkNurses = nNurses
        for i in range(0, len(encodedSetNurses), maxLenEncNurse):
            # q = min(qMax, int(math.ceil((hoursDay - initHour + 1) / (maxConsec + 1))))
            encodedNurse = encodedSetNurses[i:i + maxLenEncNurse]
            works = encodedNurse[0] >= 0.3  # if the nurse works

            if works:
                # Get the starting hour
                revers = encodedNurse[1] > propHalf  # the nurse is reversed
                if not revers:
                    prob = encodedNurse[1] / propHalf
                    initHour = ittls.dropwhile(lambda x: x[1] < prob, enumerate(firstHalf)).__next__()[0]
                else:
                    prob = (encodedNurse[1] - propHalf) / (1 - propHalf)
                    initHour = ittls.dropwhile(lambda x: x[1] < prob, enumerate(secondHalf)).__next__()[0]

                # assert 0 <= initHour <= lastInitHour
                lenEncNurse = min(maxLenEncNurse, int(math.ceil((hoursDay - initHour + 1) / (maxConsec + 1))) + 2)
                encConsecHours = encodedNurse[2:lenEncNurse]  # the chunks of consecutive hours encoded
                # assert hoursDay - initHour >= maxHours + (len(encConsecHours) - 1)
                # assert maxHours <= len(encConsecHours) * maxConsec
                workedHours = maxHours  # number of hours the nurse works
                s = sum(encConsecHours)
                normEncodedNurse = [x / s for x in encConsecHours]
                chunksHours = [0] * len(normEncodedNurse)  # length of each group of consecutive hours

                # Assign proportionally to each element of normEncodedNurse the length of a group of consecutive hours
                # chunksHours = [min(maxConsec, int(elem * workedHours)) for elem in normEncodedNurse]
                # normEncodedNurse = [normEncodedNurse[j] - chunksHours[j] / workedHours for j in range(len(normEncodedNurse))]
                for j in range(len(normEncodedNurse)):
                    chunksHours[j] = min(maxConsec, int(normEncodedNurse[j] * workedHours))
                    normEncodedNurse[j] -= chunksHours[j] / workedHours

                # Assign the remaining hours to the groups of consecutive hours that are not full
                # sortedAux = list(filter(lambda elem: chunksHours[elem[0]] < maxConsec,
                #                         sorted(enumerate(normEncodedNurse), key=lambda x: x[1], reverse=True)))
                sortedAux = sorted(enumerate(normEncodedNurse), key=lambda x: x[1], reverse=True)
                remainingHours = workedHours - sum(chunksHours)
                # I have to be sure that this will not become an infinite loop
                while remainingHours > 0:
                    # chunksHours = [chunksHours[j] + 1*(x != 0 and chunksHours[j] < maxConsec) for (j, x) in sortedAux]
                    for (j, x) in sortedAux:
                        if chunksHours[j] < maxConsec:
                            chunksHours[j] += 1
                            remainingHours -= 1
                            if remainingHours == 0:
                                break
            else:
                initHour = 0
                chunksHours = []
                revers = False
                nWorkNurses -= 1

            # Construct the nurse
            nurse = [0] * initHour
            for (j, chunk) in enumerate(filter(lambda x: x != 0, chunksHours)):
                nurse += [0] * (j != 0) + [1] * chunk
            nurse += [0] * (hoursDay - len(nurse))
            if revers:
                nurse.reverse()
            # assert len(nurse) == hoursDay
            nurses.append(nurse)

        # print()

        # calculate the dictionary we'll add to listSolutions
        # nWorkNurses = sum(sum(n) > 0 for n in nurses)
        offer = getOffer(nurses)
        uncovDemand = sum(max(0, demand[i] - offer[i]) for i in range(len(demand)))
        extraOffer = sum((offer[i] - demand[i]) ** 2 for i in range(len(demand)) if offer[i] > demand[i] + 1)
        solution = {'chr': encodedSetNurses, 'solution': nurses,
                    'fitness': uncovDemand * nNurses ** 2 + extraOffer + nWorkNurses}
        listSolutions.append(solution)

    # print("Total time", totalTime)
    offer = getOffer(listSolutions[0]['solution'])
    diff = [offer[j] - demand[j] for j in range(len(demand))]
    eprint("Diff:", diff)

    return listSolutions