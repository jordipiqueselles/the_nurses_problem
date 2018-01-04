import time
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def disableVervose(delay=0):
    time.sleep(delay)
    nullFile = open('nul', 'w')
    sys.stderr = nullFile
