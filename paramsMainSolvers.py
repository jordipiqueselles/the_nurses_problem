oplParams = {'pathToOPL': '"C:\Program Files\IBM\ILOG\CPLEX_Studio1271\opl\\bin\\x64_win64\oplrun.exe"',
             'pathToMod': "./opl_project/nurses4.mod",
             'maxMemory': 12000}

graspParams = {'numIter': 50,
               'alfa': 0.1,
               'nThreads': 8,
               'maxItWithoutImpr': 40}

brkgaParams = {'numIndividuals': 200,
               'maxGenerations': 150,
               'eliteProp': 0.1,
               'mutantsProp': 0.2,
               'inheritanceProb': 0.7,
               'maxItWithoutImpr': 50}