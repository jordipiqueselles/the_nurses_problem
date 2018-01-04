import math
import numpy as np
import time
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
        :param maxItWithoutImpr: Maximum number of iterations without finding an improvement
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

            eprint("Generation", i, "| MaxFitness", evol[-1])
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
