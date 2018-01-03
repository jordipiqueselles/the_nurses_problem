import random as rnd
import itertools as ittl


# Common parameters
hoursDay = 24

# Feasible 2 parameters
distrNNurses = (100 + i*20 for i in ittl.count())

# Feasible 1 and random generator parameters
distrMaxHours = (int(rnd.gauss(10, 1)) for _ in ittl.count())
distrMaxConsec = (int(rnd.gauss(6, 1)) for _ in ittl.count())
distrMaxPresence = (int(rnd.gauss(12, 1)) for _ in ittl.count())
distrDemand = (int(rnd.gauss(20*(i/hoursDay)+100, 5)) for i in ittl.count())

# Random generator parameters
distrMinHours = (int(rnd.gauss(4, 1)) for _ in ittl.count())
