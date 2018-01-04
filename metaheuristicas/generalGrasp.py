import os
import time
import math
import multiprocessing as mp
from functools import partial
from otherScripts.utils import eprint, disableVervose


def grasp(problem, maxIter=10, alfa=0.1, timeLimit=math.inf, maxItWithoutImpr=30):
    """
    General GRASP algorithm
    :param problem: An object representing an instance of a problem with the methods 'construct' and 'localSearch'
    :param maxIter: Maximum number of iterations
    :param alfa: Control of the randomnes. 0 no random, 1 total random
    :param timeLimit: Maximum amount of time to do the computations
    :param maxItWithoutImpr: Maximum number of iterations without finding an improvement
    :return: The best solution and the best cost
    """
    initTime = time.time()
    bestSol = None
    bestCost = math.inf
    itWithoutImpr = 0
    for i in range(maxIter):
        (sol, cost) = problem.construct(alfa)
        (sol, cost) = problem.localSearch(sol)
        eprint("Process:", os.getpid(), "Iteration:", i, "| Best cost:", bestCost)
        if cost < bestCost:
            bestSol = sol
            bestCost = cost
            itWithoutImpr = 0
        else:
            itWithoutImpr += 1

        if time.time() - initTime > timeLimit or itWithoutImpr > maxItWithoutImpr:
            break

    return bestCost, bestSol


def parallelGrasp(problem, maxIter=10, alfa=0.1, nThreads=mp.cpu_count(), timeLimit=math.inf, maxItWithoutImpr=30):
    """
    Parallel version of the GRASP algorithm
    :param problem: An object representing an instance of a problem with the methods 'construct' and 'localSearch'
    :param maxIter: Maximum number of iterations
    :param alfa: Control of the randomnes. 0 no random, 1 total random
    :param nThreads: Number of threads
    :param timeLimit: Maximum amount of time to do the computations
    :param maxItWithoutImpr: Maximum number of iterations without finding an improvement
    :return: The best solution and the best cost
    """
    with mp.Pool(nThreads) as pool:
        pool.map(disableVervose, [0.5]*nThreads)
        listResults = pool.map(partial(grasp, maxIter=1 + maxIter//nThreads, alfa=alfa, timeLimit=timeLimit,
                                       maxItWithoutImpr=maxItWithoutImpr), [problem]*nThreads)
        bestResult = min(listResults)
        return bestResult
