import sys

if '-v' not in sys.argv:
    nullFile = open('nul', 'w')
    sys.stderr = nullFile

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)