#!/usr/bin/env python

import sys, os
from ConfigParser import SafeConfigParser


def main(argv):
    sc = SafeConfigParser()
    sc.read(os.path.expanduser('~/config/parameters.cfg'))
    sc.set('RunParameters', 'state', sys.argv[1])
    sc.set('RunParameters', 'rate_type', sys.argv[2])
    sc.set('RunParameters', 'timestep', sys.argv[3])
    sc.set('RunParameters', 'direction', sys.argv[4])
    sc.set('RunParameters', 'numHH', sys.argv[5])
    sc.set('RunParameters', 'mechanism', sys.argv[6])
    sc.set('RunParameters', 'common_mask', sys.argv[7])
    with open(os.path.expanduser('~/config/parameters.cfg'), 'wb') as configFile:
        sc.write(configFile)


if __name__ == '__main__':
    main(sys.argv)
