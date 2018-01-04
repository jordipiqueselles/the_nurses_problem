import time
import sys

class mode:
    verbose = True


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def disableVervose(delay=0):
    mode.verbose = False
    time.sleep(delay)
    nullFile = open('nul', 'w')
    sys.stderr = nullFile
