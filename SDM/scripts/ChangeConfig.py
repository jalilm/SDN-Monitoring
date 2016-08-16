#!/usr/bin/env python

import sys
from ConfigParser import SafeConfigParser
from os.path import expanduser


def main(argv):
    parameters_file = expanduser("~") + '/SDN-Monitoring/config/parameters.cfg'
    sc = SafeConfigParser()
    sc.read(parameters_file)
    for arg in argv:
        sc.set('RunParameters', arg.split('=')[0].split('-')[2], arg.split('=')[1])
    with open(parameters_file, 'wb') as configFile:
        sc.write(configFile)


if __name__ == '__main__':
    main(sys.argv[1:])
