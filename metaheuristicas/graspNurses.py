import copy
import random as rnd
import itertools as ittl
import otherScripts.checkingFunctions as check


class GraspNurses:
    def __init__(self, demand, minHours, maxHours, maxConsec, maxPresence):
        self.demand = demand
        self.minHours = minHours
        self.maxHours = maxHours
        self.maxConsec = maxConsec
        self.maxPresence = maxPresence
        self.feasibleNurses = self._generateAllNurses()


    def _recursiveGenerateAllNurses(self, nurse, initHour, nHours):
        constrMaxConsec = check.getConsecHours([nurse])[0] <= self.maxConsec

        if not constrMaxConsec:
            return []

        elif nHours == 0:
            return [nurse]

        else:
            nurses = []
            for hour in range(initHour, min(initHour + 2, len(nurse) - nHours + 1)):
                auxNurse = copy.copy(nurse)
                auxNurse[hour] = 1
                nurses += self._recursiveGenerateAllNurses(auxNurse, hour + 1, nHours - 1)
            return nurses

    def _generateAllNurses(self):
        """
        Generates all the feasible working days (from the starting hour to the end one)
        :return: A matrix of feasible working days
        """
        nurses = []
        for nHours in range(self.minHours, self.maxHours+1):
            # print("Generating with nHours ->", nHours)
            nurse = [1] + [0] * (self.maxPresence - 1)
            nurses += self._recursiveGenerateAllNurses(nurse, 1, nHours - 1)

        # print("Total nurses generated:", len(nurses))
        # drop the 0s at the end
        nurses = [list(ittl.dropwhile(lambda x: x == 0, reversed(nurse))) for nurse in nurses]
        return nurses

    def _checkConstraints(self, nurse):
        """
        Check if the nurse satisfies all the constraints
        """
        # check maxHours
        constrMinMaxHours = self.minHours <= check.getNursesHours([nurse])[0] <= self.maxHours
        # check maxPresence
        constrMaxPresence = check.getPresenceHours([nurse])[0] <= self.maxPresence
        # check maxConsec
        constrMaxConsec = check.getConsecHours([nurse])[0] <= self.maxConsec
        # check resting hours
        constrRestHours = check.getRestingHours([nurse])[0] <= 1

        return constrMinMaxHours and constrMaxPresence and constrMaxConsec and constrRestHours

    @staticmethod
    def _greedyCostNurse(feasibleNurses, demand, nElems=100, nPos=5):
        """
        Calculates the greedy cost of a random nurse in some random starting points
        :param feasibleNurses: Set of feasible working days
        :param demand: Demand of nurses
        :param nElems: Number of nurses to extract from feasibleNurses
        :param nPos: Number of different starting points to try
        :return: A list of the different greedy costs calculated
        """
        listGreedyCost = []
        for _ in range(nElems):
            idx = rnd.randint(0, len(feasibleNurses) - 1)
            auxNurse = feasibleNurses[idx]
            for _ in range(nPos):
                pos = rnd.randint(0, len(demand) - len(auxNurse))
                # Create nurse. It's a deep copy of the nurse selected from feasibleNurses
                nurse = [0] * pos + auxNurse + [0] * (len(demand) - pos - len(auxNurse))
                greedyCost = sum((demand[i] * (1 - nurse[i]) for i in range(len(demand))))
                listGreedyCost.append((greedyCost, nurse))

        return listGreedyCost

    def construct(self, alfa=0.1):
        """
        Construct a solution for the problem using a randomized greedy constructive algorithm
        :param alfa: Parameter to control the randomness
        :return: The solution and its cost
        """
        nurses = []
        auxDemand = copy.copy(self.demand)

        # We don't have a solution until all the demand is satisfied
        while sum(auxDemand) > 0:
            listGreedyCost = self._greedyCostNurse(self.feasibleNurses, auxDemand)
            minCost = min(listGreedyCost)[0]
            maxCost = max(listGreedyCost)[0]
            RCL = [elem[1] for elem in listGreedyCost if elem[0] <= minCost + alfa*(maxCost - minCost)]
            randomElem = RCL[rnd.randint(0, len(RCL)-1)]
            nurses.append(randomElem)
            auxDemand = [max(0, auxDemand[i] - randomElem[i]) for i in range(len(auxDemand))]

        nNurses = len(nurses)
        return nurses, nNurses

    def _getListFreeNurses(self, nurses):
        """
        Gives a list of sets of nurses that can work for each hour
        """
        freeNurses = [set() for _ in range(len(nurses[0]))]
        for (i, nurse) in enumerate(nurses):
            for (h, work) in enumerate(nurse):
                if not work:
                    nurse[h] = 1
                    if self._checkConstraints(nurse):
                        freeNurses[h].add(i)
                    nurse[h] = 0
        return freeNurses

    def localSearch(self, nurses):
        """
        Applies local search to nurses in order to improve the cost of the solution. It tries to eliminate
        every nurse without violating any constraint
        """
        offerNurses = check.getOffer(nurses)
        extraNurses = [offerNurses[i] - self.demand[i] for i in range(len(self.demand))]
        freeNurses = self._getListFreeNurses(nurses)

        # try to eliminate every nurse
        for (i, nurse) in enumerate(nurses):
            if nurse is None:
                continue

            dictSubstitutes = {}
            canEliminate = True

            # for all hours from a nurse
            for (h, work) in enumerate(nurse):
                if work == 0 or extraNurses[h] > 0:
                    continue

                # try to assign the hours to other nurses
                for idNurse in freeNurses[h]:
                    otherNurse = nurses[idNurse]
                    otherNurse[h] = 1
                    if self._checkConstraints(otherNurse):
                        dictSubstitutes[h] = idNurse
                        break
                    else:
                        otherNurse[h] = 0

                # we couldn't find a substitute for the j-th hour
                if h not in dictSubstitutes:
                    canEliminate = False
                    break

            if canEliminate:
                # update free nurses
                for (hour, idNurse) in dictSubstitutes.items():
                    freeNurses[hour].remove(idNurse)
                for setNurses in freeNurses:
                    if i in setNurses:
                        setNurses.remove(i)

                # update extraNurses
                for (h, work) in enumerate(nurse):
                    # if the hour has been eliminated, not swapped with another nurse
                    if h not in dictSubstitutes:
                        extraNurses[h] = extraNurses[h] - work
                # "delete" nurse
                nurses[i] = None

            else:
                # reset values for modified nurses
                for (hour, idNurse) in dictSubstitutes.items():
                    nurses[idNurse][hour] = 0

        nurses = list(filter(lambda row: row is not None, nurses))
        return nurses, len(nurses)
