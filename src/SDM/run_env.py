#!/usr/bin/env python

import os
import mmap

from src.SDM.util import get_dirs, get_params, get_class
from src.SDM.NormalTest import NormalTest
from src.SDM.MonitorTest import MonitorTest
from src.SDM.TraceTest import TraceTest
from mininet.log import setLogLevel


def main():
    """
    The main code of the program, which calls the test.
    """

    "Level should be one of the following:"
    "debug, info, output, warning, error, critical"
    setLogLevel('info')

    directories = get_dirs()
    params = get_params(directories)

    with open(params['General']['sharedMemFilePath'], "wb") as _file:
        _file.write(params['General']['startGenerationToken'])

    with open(params['General']['sharedMemFilePath'], "r+b") as _file:
        mem_map = mmap.mmap(_file.fileno(), 0)

    test_class = get_class(params['RunParameters']['state'])
    print test_class
    test = test_class(mem_map, directories, params)
    #if params['RunParameters']['state'] == 'normal':
    #     test = NormalTest(mem_map, directories, params)
    # elif params['RunParameters']['state'] == 'monitor':
    #     test = MonitorTest(mem_map, directories, params)
    # elif params['RunParameters']['state'] == 'trace':
    #     test = TraceTest(mem_map, directories, params)
    # else:
    #     os.remove(params['General']['sharedMemFilePath'])
    #     mem_map.close()
    #     raise Exception('Please provide a valid test at' +
    #                     ' state configuration in parameters.cfg')
    test.run()
    test.merge_logs()
    os.remove(params['General']['sharedMemFilePath'])
    mem_map.close()


if __name__ == '__main__':
    main()
