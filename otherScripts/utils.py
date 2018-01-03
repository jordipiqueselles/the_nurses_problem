import time
import sys
import multiprocessing as mp
import math


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def disableVervose(delay=0):
    # eprint("Disabling verbose")
    time.sleep(delay)
    nullFile = open('nul', 'w')
    sys.stderr = nullFile
    # eprint("Verbose disabled")

#####################################################################
#####################################################################

def f(x):
    for i in range(1000):
        x = math.log(i+1)
    x = mp.current_process().pid
    return x


if __name__ == '__main__':
    t = time.time()
    pool = mp.Pool(8)
    l = pool.map(f, range(300000))
    pool.close()
    # l = list(map(f, range(300000)))
    print("Time:", time.time() - t)
    s = set(l)
    for elem in s:
        print(elem, "->", l.count(elem))