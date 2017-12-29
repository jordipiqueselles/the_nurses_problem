import math
import numpy as np
import matplotlib.pyplot as plt
import logging
import time
import itertools as ittls
from otherScripts.checkingFunctions import *
from otherScripts.utils import eprint


class Brkga:
    def __init__(self, decode):
        """
        :param decode: Decoder for the problem
        """
        self.decode = decode
        self.population = []

    def run(self, data, chrLength, numIndividuals=100, maxGenerations=100, eliteProp=0.1, mutantsProp=0.2,
            inheritanceProb=0.7, timeLimit=math.inf, maxItWithoutImpr=50):
        """
        Executes the BRKGA algorithm
        :param data: Data defining the problem. It's a dictionary of parameters.
        :param chrLength: Length of the chromosome for an individual
        :param numIndividuals: Number of individuals in the population
        :param maxGenerations: Maximum number of generations
        :param eliteProp: Proportion of individuals that will belong to the elite segment
        :param mutantsProp: Proportion of mutants generated at each iteration
        :param inheritanceProb: Probability of inheriting from an elite individual
        :param timeLimit: Maximum amount of time to do the computations
        :return: The best individual found
        """

        initTime = time.time()

        # Get numElite, numMutants and numCrossover from the proportions
        numElite = int(math.ceil(numIndividuals * eliteProp))
        numMutants = int(math.ceil(numIndividuals * mutantsProp))
        numCrossover = max(numIndividuals - numElite - numMutants, 0)

        self.population = self._initializePopulation(numIndividuals, chrLength)
        evol = [math.inf]
        itWithoutImpr = 0

        for i in range(maxGenerations):
            self.population = self.decode(self.population, data)
            evol.append(self._getBestFitness()['fitness'])

            offer = getOffer(self._getBestFitness()['solution'])
            diff = [offer[j] - data['demand'][j] for j in range(len(data['demand']))]

            eprint("Generation", i, "| MaxFitness", evol[-1], "| Diff:", diff)
            if evol[-2] > evol[-1]:
                itWithoutImpr = 0
            else:
                itWithoutImpr += 1

            elite, nonelite = self._classifyIndividuals(numElite)
            mutants = self._generateMutantIndividuals(numMutants, chrLength)
            crossover = self._doCrossover(elite, nonelite, inheritanceProb, numCrossover)
            self.population = elite + crossover + mutants

            if time.time() - initTime > timeLimit or itWithoutImpr > maxItWithoutImpr:
                break

        self.population = self.decode(self.population, data)
        bestIndividual = self._getBestFitness()

        # plt.plot(evol)
        # plt.xlabel('number of generations')
        # plt.ylabel('Fitness of best individual')
        # plt.axis([0, len(evol), 0, (chrLength + 1) * chrLength / 2])
        # plt.show()

        eprint("Best individual:", bestIndividual)

        bestSolution = bestIndividual['solution']
        bestCost = sum(sum(nurse) != 0 for nurse in bestSolution)
        return bestCost, bestSolution

    @staticmethod
    def _initializePopulation(numIndividuals, chrLength):
        """
        Initialize the population randomly
        :param numIndividuals: Number of individuals to generate
        :param chrLength: Length of the chromosome of one individual
        :return: The generated population
        """
        population = []
        for i in range(numIndividuals):
            chromosome = list(np.random.rand(chrLength))
            population.append({'chr': chromosome, 'solution': {}, 'fitness': None})
        return population

    def _classifyIndividuals(self, numElite):
        """
        Classifies the population between elite members and non-elite
        :param numElite: Number of individuals that will be considered as elite
        :return: A tuple. The first element is the list of elite elements and the second is the list of non-elite
        """
        fitness = np.array([e['fitness'] for e in self.population])
        order = sorted(range(len(fitness)), key=lambda k: fitness[k])
        whichElite = order[0:numElite]
        whichNonElite = order[numElite:(len(fitness))]
        population = np.array(self.population)
        elite = population[whichElite]
        nonElite = population[whichNonElite]
        return list(elite), list(nonElite)

    @staticmethod
    def _generateMutantIndividuals(numMutants, chrLength):
        """
        Generates some mutant elements
        :param numMutants: Number of mutants to generate
        :param chrLength: Length of the chromosome of one individual
        :return: The mutants generated
        """
        mutants = []
        for i in range(numMutants):
            chromosome = list(np.random.rand(chrLength))
            mutants.append({'chr': chromosome, 'solution': {}, 'fitness': None})
        return mutants

    @staticmethod
    def _doCrossover(elite, nonelite, ro, numCrossover):
        """
        Do the crossover to create a new generation
        :param elite: Elite individuals
        :param nonelite: Non-elite individuals
        :param ro: Probability of inheriting from an elite element
        :param numCrossover: Number of new elements generated using crossover
        :return: The crossover elements generated
        """
        crossover = []
        for i in range(numCrossover):
            indexElite = int(math.floor(np.random.rand() * len(elite)))
            indexNonElite = int(math.floor(np.random.rand() * len(nonelite)))
            chrElite = elite[indexElite]['chr']
            chrNonElite = nonelite[indexNonElite]['chr']
            rnd = list(np.random.rand(len(chrElite)))
            chrCross = [chrElite[i] if rnd[i] <= ro else chrNonElite[i] for i in range(len(chrElite))]
            crossover.append({'chr': chrCross, 'solution': {}, 'fitness': None})
        return crossover

    def _getBestFitness(self):
        """
        :return: The best individual in the population
        """
        bestFit = min(self.population, key=lambda x: x['fitness'])
        return bestFit


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


def createProportionDemand(demand, maxPresence, maxHours, lastInitHour):
    l = len(demand)
    prop = [0] * l
    for i in range(lastInitHour):
        for j in range(i, min(i + maxPresence, l)):
            prop[j] += 1
            prop[l - 1 - j] += 1

    # print(prop)
    auxDemand = [demand[i] / prop[i] for i in range(l)]

    sumIni = sum(auxDemand[:(l + 1) // 2])
    sumFi = sum(auxDemand[(l + 1) // 2:])
    # print([round(elem/sumIni, 2) for elem in auxDemand[:(l+1)//2]] + [round(elem/sumFi, 2) for elem in auxDemand[(l+1)//2:]])
    sumAuxDemand = auxDemand + []
    for i in range(1, (l + 1) // 2):
        sumAuxDemand[i] += sumAuxDemand[i - 1]
        sumAuxDemand[l - i - 1] += sumAuxDemand[l - i]
    firstHalf = [elem / sumIni for elem in sumAuxDemand[:(l + 1) // 2]]
    secondHalf = [elem / sumFi for elem in reversed(sumAuxDemand[(l + 1) // 2:])]
    # print(sumAuxDemand)
    return sumIni / (sumIni + sumFi), firstHalf, secondHalf


def createProportionDemand2(demand, maxPresence, maxHours, lastInitHour):
    l = len(demand)
    maxPresence = min(maxPresence, l)
    r = round(maxHours / maxPresence, 1)
    npDemand = np.array([demand]).transpose()
    matrix = np.zeros((l, l))
    for (i, row) in enumerate(matrix):
        if lastInitHour < i < (l-lastInitHour):
            continue
        row[i] = 1
        if i < l//2:
            for j in range(i+1, min(i+maxPresence, l)):
                row[j] = r
        else:
            for j in range(i-1, max(i-maxPresence, 0), -1):
                row[j] = r

    matrix = matrix.transpose()
    for row in matrix:
        print(row.tolist())
    print(np.linalg.matrix_rank(matrix))
    prob = np.linalg.solve(matrix, npDemand)
    prob /= sum(prob)
    return prob

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

    print([round(p, 2) for p in prob])
    sumIni = sum(prob[:(l + 1) // 2])
    sumFi = sum(prob[(l + 1) // 2:])
    for i in range(1, (l + 1) // 2):
        prob[i] += prob[i - 1]
        prob[l - i - 1] += prob[l - i]
    firstHalf = [elem / sumIni for elem in prob[:(l + 1) // 2]]
    secondHalf = [elem / sumFi for elem in reversed(prob[(l + 1) // 2:])]

    print([round(p, 2) for p in firstHalf])
    print([round(p, 2) for p in secondHalf])
    return sumIni / (sumIni + sumFi), firstHalf, secondHalf


def proves3():
    demand = [5, 3, 3, 3, 4, 4, 7, 10, 13, 22, 38, 48, 48, 48, 26, 0, 8, 6, 12, 4, 13, 10, 11, 14]
    maxPresence = 11
    maxHours = 8
    # prop = createProportionDemand(demand, maxPresence, 10)
    # print(prop)
    # matrix = createProportionDemand2(demand, maxPresence, maxHours, 10)
    # for row in matrix:
    #     print(row.tolist())
    # prob = createProportionDemand2(demand, maxPresence, maxHours, 13)
    # print(prob.tolist())
    (p, f, s) = createProportionDemand3(demand, maxPresence, maxHours, 13)
    print([round(p, 2) for p in f])
    print([round(p, 2) for p in s])


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
        for i in range(0, len(encodedSetNurses), maxLenEncNurse):
            # q = min(qMax, int(math.ceil((hoursDay - initHour + 1) / (maxConsec + 1))))
            encodedNurse = encodedSetNurses[i:i + maxLenEncNurse]
            works = encodedNurse[0] >= 0.3  # if the nurse works

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

            if works:
                # Assign proportionally to each element of normEncodedNurse the length of a group of consecutive hours
                for j in range(len(normEncodedNurse)):
                    chunksHours[j] = min(maxConsec, int(normEncodedNurse[j] * workedHours))
                    if chunksHours[j] == maxConsec:
                        normEncodedNurse[j] = 0
                    else:
                        normEncodedNurse[j] -= chunksHours[j] / workedHours

                # Assign the remaining hours to the groups of consecutive hours that are not full
                sortedAux = list(filter(lambda elem: elem[1] != 0,
                                        sorted(enumerate(normEncodedNurse), key=lambda x: x[1], reverse=True)))
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
        nWorkNurses = sum(sum(n) > 0 for n in nurses)
        offer = getOffer(nurses)
        uncovDemand = sum(max(0, demand[i] - offer[i]) for i in range(len(demand)))
        extraOffer = sum((offer[i] - demand[i]) ** 2 for i in range(len(demand)) if offer[i] > demand[i] + 1)
        solution = {'chr': encodedSetNurses, 'solution': nurses,
                    'fitness': uncovDemand * nNurses ** 2 + extraOffer + nWorkNurses}
        listSolutions.append(solution)

    # print("Total time", totalTime)
    return listSolutions


def proves():
    params = dict()
    params['hoursDay'] = 24
    params["maxHours"] = 8
    params["maxConsec"] = 4
    params["maxPresence"] = 23
    params["demand"] = [0] * params['hoursDay']
    params["minHours"] = 4
    params['nNurses'] = 100

    lenChr = getChrLength(params)
    ind = dict()
    ind['chr'] = np.random.rand(lenChr)

    listNurses = decode([ind], params)
    for elem in listNurses:
        nurses = elem['solution']
        print(answerSatisfiesConstr(nurses, params))
        print(getOffer(nurses))


def proves2():
    # best cost -> 288
    params = dict()
    params['hoursDay'] = 24
    params["maxHours"] = 8
    params["maxConsec"] = 4
    params["maxPresence"] = 10
    params["demand"] = [elem * (params['hoursDay'] - elem) for elem in range(params['hoursDay'])]
    params["minHours"] = 4
    params['nNurses'] = 300

    print(params['demand'])

    solver = Brkga(decode)
    (cost, nurses) = solver.run(params, getChrLength(params), numIndividuals=200, maxGenerations=200,
                                maxItWithoutImpr=100)

    for nurse in nurses:
        print(nurse)
    print()
    print(answerSatisfiesConstr(nurses, params))
    print(params['demand'])
    print(getOffer(nurses))
    print("Cost:", cost)


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    # logging.debug('hola')
    # logging.info('adeu')
    proves2()
