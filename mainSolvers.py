from paramsMainSolvers import *
from otherScripts.autoExecution import *
from otherScripts.utils import *


def usage():
    print("Usage:")
    print('python3 mainSolvers.py "folderWithInstances" "solver" [options]')
    print("The solver can be 'grasp', 'brkga' or 'opl'")
    print("Options:")
    print("-v Verbose mode")
    print("-h Show the usage")
    print("-w Write the results in a file")
    print('-t "number" Maximum amount of time for the solver in minutes')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Not enough arguments")
        usage()
        exit(1)

    if "-h" in sys.argv:
        usage()
        exit(0)

    # Data folder
    dataFolder = sys.argv[1]
    try:
        os.listdir(dataFolder)
    except FileNotFoundError:
        print("The data folder", dataFolder, "doesn't exists")
        exit(1)
    if dataFolder[-1] != '/':
        dataFolder = dataFolder + '/'

    # Solver
    if sys.argv[2] == 'grasp':
        solver = executeGrasp
        params = graspParams
    elif sys.argv[2] == 'brkga':
        solver = executeBrkga
        params = brkgaParams
    elif sys.argv[2] == 'opl':
        solver = executeOpl
        params = oplParams
    else:
        print('Unsuported solver', sys.argv[2])
        exit(1)

    # Max time (seconds) for solving one instance
    if "-t" in sys.argv:
        idxTime = sys.argv.index("-t") + 1
        try:
            maxTime = float(sys.argv[idxTime])
        except ValueError:
            print("Invalid value for time", sys.argv[idxTime])
            exit(1)
        sys.argv.remove(sys.argv[idxTime])
        sys.argv.remove('-t')
    else:
        maxTime = math.inf

    # verbose
    if '-v' not in sys.argv:
        disableVervose()
    else:
        sys.argv.remove('-v')

    # write results in a file
    if '-w' in sys.argv:
        fileName = "./results"
        sys.argv.remove('-w')
    else:
        fileName = None

    if len(sys.argv) > 3:
        print("Invalid option:", sys.argv[3])
        exit(1)

    executeSolver(dataFolder, solver, maxTime, params, fileName)