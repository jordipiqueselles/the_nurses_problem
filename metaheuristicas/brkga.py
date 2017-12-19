import math
import numpy as np
import matplotlib.pyplot as plt
import logging
from otherScripts.checkingFunctions import *


class Brkga:
    def __init__(self, decode):
        self.decode = decode
        self.population = []

    def run(self, data, chrLength, numIndividuals=100, maxGenerations=100, eliteProp=0.1, mutantsProp=0.2,
            inheritanceProp=0.7, verb=True):

        # Get numElite, numMutants and numCrossover from the proportions
        numElite = int(math.ceil(numIndividuals * eliteProp))
        numMutants = int(math.ceil(numIndividuals * mutantsProp))
        numCrossover = max(numIndividuals - numElite - numMutants, 0)

        self.population = self._initializePopulation(numIndividuals, chrLength)
        evol = []

        for i in range(maxGenerations):
            self.population = self.decode(self.population, data)
            evol.append(self._getBestFitness()['fitness'])
            if verb:
                print("Generation", i, "| MaxFitness", evol[-1])

            elite, nonelite = self._classifyIndividuals(numElite)
            mutants = self._generateMutantIndividuals(numMutants, chrLength)
            crossover = self._doCrossover(elite, nonelite, inheritanceProp, numCrossover)
            self.population = elite + crossover + mutants

        self.population = self.decode(self.population, data)
        bestIndividual = self._getBestFitness()

        if verb:
            plt.plot(evol)
            plt.xlabel('number of generations')
            plt.ylabel('Fitness of best individual')
            plt.axis([0, len(evol), 0, (chrLength + 1) * chrLength / 2])
            plt.show()

            print(bestIndividual)

        return bestIndividual

    @staticmethod
    def _initializePopulation(numIndividuals, chrLength):
        population = []
        for i in range(numIndividuals):
            chromosome = list(np.random.rand(chrLength))
            population.append({'chr': chromosome, 'solution': {}, 'fitness': None})
        return population

    def _classifyIndividuals(self, numElite):
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
        mutants = []
        for i in range(numMutants):
            chromosome = list(np.random.rand(chrLength))
            mutants.append({'chr': chromosome, 'solution': {}, 'fitness': None})
        return mutants

    @staticmethod
    def _doCrossover(elite, nonelite, ro, numCrossover):
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
        # fitness = np.array([e['fitness'] for e in population])
        # order = sorted(range(len(fitness)), key=lambda k: fitness[k])
        # return population[order[0]]
        bestFit = min(self.population, key=lambda x: x['fitness'])
        return bestFit


def getChrLength(params):
    # Max number of groups of consecutive working hours
    maxNumGroupConsecH = min(params['maxPresence'] - params['maxHours'] + 1, params['maxHours']*2 - 1)
    # Length of an encoded nurse
    legthEncodedNurse = maxNumGroupConsecH + 2
    return params['numNurses'] * legthEncodedNurse


def decode(population, params, verbose=False):
    hoursDay = params['hoursDay']
    minHours = params["minHours"]
    maxHours = params["maxHours"]
    maxConsec = params["maxConsec"]
    maxPresence = params["maxPresence"]
    demand = params["demand"]
    numNurses = params['numNurses']

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
            if verbose:
                print(nurse, sum(nurse))
            nurses.append(nurse)

        if verbose:
            print()

        # calculate the dictionary we'll add to listSolutions
        nWorkNurses = sum(sum(n) > 0 for n in nurses)
        offer = getOffer(nurses)
        uncovDemand = sum(max(0, demand[i] - offer[i]) for i in range(len(demand)))
        solution = {'chr': encodedSetNurses, 'solution': nurses, 'fitness': uncovDemand*numNurses + nWorkNurses}
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
    params['numNurses'] = 100

    lenChr = getChrLength(params)
    ind = dict()
    ind['chr'] = np.random.rand(lenChr)

    listNurses = decode([ind], params, verbose=True)
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
    params['numNurses'] = 300

    solver = Brkga(decode)
    solution = solver.run(params, getChrLength(params), numIndividuals=200, maxGenerations=400)
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
