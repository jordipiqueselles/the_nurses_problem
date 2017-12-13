import math
import multiprocessing as mp
from functools import partial


def grasp(problem, maxIter=10, alfa=0.1):
    """
    General GRASP algorithm
    :param problem: An object representing an instance of a problem with the methods 'construct' and 'localSearch'
    :param maxIter: Maximum number of iterations
    :param alfa: Control of the randomnes. 0 no random, 1 total random
    :return: The best solution and the best cost
    """
    bestSol = None
    bestCost = math.inf
    for i in range(maxIter):
        # print("Iteration", i)
        (sol, cost) = problem.construct(alfa)
        (sol, cost) = problem.localSearch(sol)
        if cost < bestCost:
            bestSol = sol
            bestCost = cost
    return bestCost, bestSol


def parallelGrasp(problem, maxIter=10, alfa=0.1, nThreads=mp.cpu_count()):
    with mp.Pool(nThreads) as pool:
        # def auxGrasp(i):
        #     return grasp(params, construct, localSearch, 1 + maxIter // nThreads, alfa)
        # listResults = pool.map(auxGrasp, range(nThreads))
        listResults = pool.map(partial(grasp, maxIter=1 + maxIter//nThreads, alfa=alfa), [problem]*nThreads)
        bestResult = min(listResults)
        return bestResult


if __name__ == '__main__':
    pass
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
