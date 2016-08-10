#!/usr/bin/env python

import os
import sys
from ConfigParser import SafeConfigParser


def main(argv):
    argsdict = {}
    sc = SafeConfigParser()
    sc.read(os.path.expanduser('~/config/parameters.cfg'))
    for farg in sys.argv:
        if farg.startswith('--'):
            (arg, val) = farg.split("=")
            arg = arg[2:]
            if arg not in argsdict:
                sc.set('RunParameters', arg, val)
    with open(os.path.expanduser('~/config/parameters.cfg'), 'wb') as configFile:
        sc.write(configFile)

if __name__ == '__main__':
    main(sys.argv)
