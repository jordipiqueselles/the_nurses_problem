import time
import math
import multiprocessing as mp
from functools import partial
import metaheuristicas.graspNurses as graspNurses


def grasp(problem, maxIter=10, alfa=0.1, verb=True, timeLimit=math.inf):
    """
    General GRASP algorithm
    :param problem: An object representing an instance of a problem with the methods 'construct' and 'localSearch'
    :param maxIter: Maximum number of iterations
    :param alfa: Control of the randomnes. 0 no random, 1 total random
    :param verb: Activate verbose mode
    :param timeLimit: Maximum amount of time to do the computations
    :return: The best solution and the best cost
    """
    initTime = time.time()
    bestSol = None
    bestCost = math.inf
    for i in range(maxIter):
        if verb:
            print("Iteration", i)
        (sol, cost) = problem.construct(alfa)
        (sol, cost) = problem.localSearch(sol)
        if cost < bestCost:
            bestSol = sol
            bestCost = cost

        if (time.time() - initTime) / 1000 > timeLimit:
            break

    return bestCost, bestSol


def parallelGrasp(problem, maxIter=10, alfa=0.1, nThreads=mp.cpu_count(), verb=True, timeLimit=math.inf):
    """
    Parallel version of the GRASP algorithm
    :param problem: An object representing an instance of a problem with the methods 'construct' and 'localSearch'
    :param maxIter: Maximum number of iterations
    :param alfa: Control of the randomnes. 0 no random, 1 total random
    :param nThreads: Number of threads
    :param verb: Activate verbose mode
    :param timeLimit: Maximum amount of time to do the computations
    :return: The best solution and the best cost
    """
    with mp.Pool(nThreads) as pool:
        listResults = pool.map(partial(grasp, maxIter=1 + maxIter//nThreads, alfa=alfa, verb=verb, timeLimit=timeLimit),
                               [problem]*nThreads)
        bestResult = min(listResults)
        return bestResult


def prova1():
    hoursDay = 24
    maxHours = 8
    maxConsec = 4
    maxPresence = 10
    demand = [elem * (hoursDay - elem) for elem in range(hoursDay)]
    minHours = 4
    numNurses = 300

    problem = graspNurses.GraspNurses(demand, minHours, maxHours, maxConsec, maxPresence)
    t = time.time()
    (bestCost, bestResult) = parallelGrasp(problem, maxIter=500)
    print("Time:", time.time() - t)
    print(bestCost)


if __name__ == '__main__':
    prova1()

    # from data_generators.generator import generateFeasible2, generateFeasible1
    # from otherScripts.autoExecution import getParams
    #
    # # random generators for the different variables of an instance of the problem
    # distrMinHours = (int(rnd.gauss(4, 1)) for _ in ittl.count())
    # distrMaxHours = (int(rnd.gauss(10, 1)) for _ in ittl.count())
    # distrMaxConsec = (int(rnd.gauss(6, 1)) for _ in ittl.count())
    # distrMaxPresence = (int(rnd.gauss(12, 1)) for _ in ittl.count())
    # distrDemand = (int(rnd.gauss(150, 20)) for _ in ittl.count())
    #
    # # (params, sol) = generateFeasible2(200)
    # # (params, oldSol) = generateFeasible1(distrDemand)
    # # print("Cost generator ->", len(oldSol))
    # # (sol, cost) = constructNurses(params, 0.1)
    # # print(params["demand"])
    # # print(getOffer(sol))
    # # print(answerSatisfiesConstr(sol, params))
    # # print("Cost constructor ->", cost)
    # # (sol, cost) = localSearchNurses(sol, params)
    # # print(answerSatisfiesConstr(sol, params))
    # # print("Cost local search ->", cost)
    # # exit(0)
    #
    # for _ in range(20):
    #     # (params, oldSol) = generateFeasible1(distrDemand)
    #     # print("Cost generator ->", len(oldSol))
    #     params = getParams('../data_generators/autoGeneratedData/feasible2_3.dat')
    #
    #     (sol, cost) = constructNurses(params, 0.1)
    #     ok = answerSatisfiesConstr(sol, params)
    #     print(ok)
    #     assert ok[0]
    #     print("Cost constructor ->", cost)
    #
    #     (sol, cost) = localSearchNurses(sol, params)
    #     ok = answerSatisfiesConstr(sol, params)
    #     print(ok)
    #     assert ok[0]
    #     print("Cost local search ->", cost)
    #
    #     print()

    # for _ in range(20):
    #     (params, oldSol) = generateFeasible1(distrDemand)
    #     print(params)
    #     oldCost = len(oldSol)
    #     print(oldCost)
    #
    #     (sol, cost) = localSearchNurses(copy.copy(oldSol), params)
    #     print(sol)
    #     print(cost)
    #     sat = answerSatisfiesConstr(sol, params)
    #     print(sat)
    #     assert all(sat[1][1:])
    #
    #     # (sol, cost) = localSearchNurse(copy.copy(oldSol), params)
    #     # print(sol)
    #     # print(cost)
    #     # sat = answerSatisfiesConstr(sol, params)
    #     # print(sat)
    #     # assert all(sat[1][1:])
    #
    #     print()
