#!/usr/bin/env python

import sys
from ConfigParser import SafeConfigParser
from os.path import expanduser


def main(argv):
    parameters_file = expanduser("~") + '/SDN-Monitoring/config/parameters.cfg'
    sc = SafeConfigParser()
    sc.read(parameters_file)
    sc.set('RunParameters', 'state', argv[1])
    sc.set('RunParameters', 'rate_type', argv[2])
    sc.set('RunParameters', 'timestep', argv[3])
    sc.set('RunParameters', 'direction', argv[4])
    sc.set('RunParameters', 'numHH', argv[5])
    sc.set('RunParameters', 'mechanism', argv[6])
    sc.set('RunParameters', 'common_mask', argv[7])
    with open(parameters_file, 'wb') as configFile:
        sc.write(configFile)


if __name__ == '__main__':
    main(sys.argv)
