import math
import numpy as np
import matplotlib.pyplot as plt
from otherScripts.checkingFunctions import answerSatisfiesConstr


class Brkga:
    def __init__(self, numIndividuals, chrLength, decoder):
        self.numIndividuals = numIndividuals
        self.chrLength = chrLength
        self.decoder = decoder
        self.population = self._initializePopulation()


    def run(self, maxGenerations, data):
        evol = []
        for _ in range(maxGenerations):
            self.population = self.decoder.decode(self.population, data)
            evol.append(self.getBestFitness(self.population)['fitness'])
            if numElite > 0:
                elite, nonelite = self.classifyIndividuals(self.population, numElite)
            else:
                elite = []
                nonelite = self.population
            if numMutants > 0:
                mutants = self.generateMutantIndividuals(numMutants, chrLength)
            else:
                mutants = []
            if numCrossover > 0:
                crossover = self.doCrossover(elite, nonelite, ro, numCrossover)
            else:
                crossover = []
            population = elite + crossover + mutants

        population = self.decoder.decode(population, data)
        bestIndividual = self.getBestFitness(population)
        plt.plot(evol)
        plt.xlabel('number of generations')
        plt.ylabel('Fitness of best individual')
        plt.axis([0, len(evol), 0, (self.chrLength + 1) * self.chrLength / 2])
        plt.show()

        print(bestIndividual)

    def _initializePopulation(self):
        population = []
        for i in range(self.numIndividuals):
            chromosome = list(np.random.rand(self.chrLength))
            population.append({'chr': chromosome, 'solution': {}, 'fitness': None})
        return population


    def classifyIndividuals(population, numElite):
        fitness = np.array([e['fitness'] for e in population])
        order = sorted(range(len(fitness)), key=lambda k: fitness[k])
        whichElite = order[0:numElite]
        whichNonElite = order[numElite:(len(fitness))]
        population = np.array(population)
        elite = population[whichElite]
        nonElite = population[whichNonElite]
        return list(elite), list(nonElite)


    def generateMutantIndividuals(numMutants, chrLength):
        mutants = []
        for i in range(numMutants):
            chromosome = list(np.random.rand(chrLength))
            mutants.append({'chr': chromosome, 'solution': {}, 'fitness': None})
        return mutants


    def doCrossover(elite, nonelite, ro, numCrossover):
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


    def getBestFitness(population):
        fitness = np.array([e['fitness'] for e in population])
        order = sorted(range(len(fitness)), key=lambda k: fitness[k])
        return population[order[0]]


def decoder(population, params):
    hoursDay = params['hoursDay']
    maxHours = params["maxHours"]
    maxConsec = params["maxConsec"]
    maxPresence = params["maxPresence"]

    qMax = int(math.ceil((maxPresence + 1) / (maxConsec + 1)))
    lastInitHour = hoursDay - maxPresence

    listNurses = []
    for elem in population:
        nurses = []
        for i in range(0, len(elem), qMax+1):
            encodedNurse = elem[i:i+qMax+1]
            initHour = int(round(encodedNurse[0] * lastInitHour, 0))
            workedHours = maxHours
            s = sum(encodedNurse[1:])
            aux = [x/s for x in encodedNurse[1:]]
            chunksHours = [0] * len(aux)
            for j in range(len(aux)):
                chunksHours[j] = min(maxConsec, int(aux[j]*workedHours))
                if chunksHours[j] == maxConsec:
                    aux[j] = 0
                else:
                    aux[j] -= chunksHours[j] * workedHours

            sortedAux = sorted(enumerate(aux), key=lambda x: x[1], reverse=True)
            remainingHours = workedHours - sum(chunksHours)
            for j in range(remainingHours):
                if sortedAux[j][1] == 0:
                    break
                else:
                    chunksHours[sortedAux[j][0]] += 1

            nurse = [0] * initHour
            for chunk in chunksHours:
                nurse += [1] * chunk + [0]
            nurse += [0] * hoursDay
            nurse = nurse[:hoursDay]
            print(nurse)
            nurses.append(nurse)

        print()
        listNurses.append(nurses)

    return listNurses


def proves():
    params = {}
    params['hoursDay'] = 24
    params["maxHours"] = 8
    params["maxConsec"] = 4
    params["maxPresence"] = 10
    params["demand"] = [0] * params['hoursDay']
    params["minHours"] = 4
    params['numNurses'] = 100

    qMax = int(math.ceil((params["maxPresence"] + 1) / (params["maxConsec"] + 1)))
    population = np.random.rand((qMax+1)*params['numNurses'])

    listNurses = decoder([population], params)
    for nurses in listNurses:
        print(answerSatisfiesConstr(nurses, params))

proves()