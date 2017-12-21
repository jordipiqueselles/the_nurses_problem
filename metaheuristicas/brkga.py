import math
import numpy as np
import matplotlib.pyplot as plt
import logging
import time
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
            inheritanceProb=0.7, timeLimit=math.inf):
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
        evol = []

        for i in range(maxGenerations):
            self.population = self.decode(self.population, data)
            evol.append(self._getBestFitness()['fitness'])
            eprint("Generation", i, "| MaxFitness", evol[-1])

            elite, nonelite = self._classifyIndividuals(numElite)
            mutants = self._generateMutantIndividuals(numMutants, chrLength)
            crossover = self._doCrossover(elite, nonelite, inheritanceProb, numCrossover)
            self.population = elite + crossover + mutants

            if time.time() - initTime > timeLimit:
                break

        self.population = self.decode(self.population, data)
        bestIndividual = self._getBestFitness()

        # plt.plot(evol)
        # plt.xlabel('number of generations')
        # plt.ylabel('Fitness of best individual')
        # plt.axis([0, len(evol), 0, (chrLength + 1) * chrLength / 2])
        # plt.show()

        eprint("Best individual:", bestIndividual)

        return bestIndividual

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
    # Max number of groups of consecutive working hours
    maxNumGroupConsecH = min(params['maxPresence'] - params['maxHours'] + 1, params['maxHours']*2 - 1)
    # Length of an encoded nurse
    legthEncodedNurse = maxNumGroupConsecH + 2
    return params['nNurses'] * legthEncodedNurse


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
    maxHours = min(maxHours, maxPresence - maxPresence//maxConsec)
    # Max number of groups of consecutive working hours
    maxNumGroupConsecH = min(maxPresence - maxHours + 1, maxHours*2 - 1)
    # Max length of an encoded nurse
    maxLenEncNurse = maxNumGroupConsecH + 2
    # Last hour when the working day of a nurse can start
    # lastInitHour = hoursDay - maxPresence
    lastInitHour = hoursDay - maxHours - math.ceil(maxHours/maxConsec) + 1

    listSolutions = []
    populationChr = (ind['chr'] for ind in population)
    for encodedSetNurses in populationChr:
        nurses = []
        for i in range(0, len(encodedSetNurses), maxLenEncNurse):
            # q = min(qMax, int(math.ceil((hoursDay - initHour + 1) / (maxConsec + 1))))
            encodedNurse = encodedSetNurses[i:i+maxLenEncNurse]
            works = encodedNurse[0] >= 0.5  # if the nurse works
            initHour = int(round(encodedNurse[1] * lastInitHour, 0))  # the hour she starts working
            lenEncNurse = min(maxLenEncNurse, int(math.ceil((hoursDay - initHour)/maxConsec)) + 2)
            encConsecHours = encodedNurse[2:lenEncNurse]  # the chunks of consecutive hours encoded
            workedHours = maxHours  # number of hours the nurse works
            s = sum(encConsecHours)
            normEncodedNurse = [x/s for x in encConsecHours]
            chunksHours = [0] * len(normEncodedNurse)  # length of each group of consecutive hours

            if works:
                # Assign proportionally to each element of normEncodedNurse the length of a group of consecutive hours
                for j in range(len(normEncodedNurse)):
                    chunksHours[j] = min(maxConsec, int(normEncodedNurse[j]*workedHours))
                    if chunksHours[j] == maxConsec:
                        normEncodedNurse[j] = 0
                    else:
                        normEncodedNurse[j] -= chunksHours[j] / workedHours

                # Assign the remaining hours to the groups of consecutive hours that are not full
                sortedAux = sorted(enumerate(normEncodedNurse), key=lambda x: x[1], reverse=True)
                remainingHours = workedHours - sum(chunksHours)
                # I have to be sure that this will not become an infinite loop
                while remainingHours > 0:
                    for (j, x) in sortedAux:
                        if x != 0 and chunksHours[j] < maxConsec:
                            chunksHours[j] += 1
                            remainingHours -= 1
                            if remainingHours == 0:
                                break

            # Construct the nurse
            nurse = [0] * initHour
            for chunk in chunksHours:
                if chunk != 0:
                    nurse += [1] * chunk + [0]
            nurse += [0] * hoursDay
            nurse = nurse[:hoursDay]
            # print(nurse, sum(nurse))
            nurses.append(nurse)

        # print()

        # calculate the dictionary we'll add to listSolutions
        nWorkNurses = sum(sum(n) > 0 for n in nurses)
        offer = getOffer(nurses)
        uncovDemand = sum(max(0, demand[i] - offer[i]) for i in range(len(demand)))
        solution = {'chr': encodedSetNurses, 'solution': nurses, 'fitness': uncovDemand*(nNurses+1) + nWorkNurses}
        listSolutions.append(solution)

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
    params = dict()
    params['hoursDay'] = 24
    params["maxHours"] = 8
    params["maxConsec"] = 4
    params["maxPresence"] = 10
    params["demand"] = [elem*(params['hoursDay'] - elem) for elem in range(params['hoursDay'])]
    params["minHours"] = 4
    params['nNurses'] = 300

    solver = Brkga(decode)
    solution = solver.run(params, getChrLength(params), numIndividuals=200, maxGenerations=300)
    nurses = solution['solution']

    for nurse in nurses:
        print(nurse)
    print()
    print(answerSatisfiesConstr(nurses, params))
    print(params['demand'])
    print(getOffer(nurses))


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    # logging.debug('hola')
    # logging.info('adeu')
    proves2()
