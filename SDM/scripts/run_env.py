#!/usr/bin/env python

import logging
import mmap
import os

from mininet.log import setLogLevel

from SDM.util import get_dirs, get_params, get_class


def main():
    """
    The main code of the program, which calls the test.
    """

    logger = logging.getLogger(__name__)

    "Level should be one of the following:"
    "debug, info, output, warning, error, critical"
    # setLogLevel('debug')
    setLogLevel(logging.getLevelName(logger.getEffectiveLevel()).lower())

    directories = get_dirs()
    params = get_params(directories)

    with open(params['General']['sharedMemFilePath'], "wb") as _file:
        logger.debug("Opened shared memory file to write start of generation token")
        _file.write(params['General']['startGenerationToken'])

    with open(params['General']['sharedMemFilePath'], "r+b") as _file:
        mem_map = mmap.mmap(_file.fileno(), 0)

    test_class = get_class(params['RunParameters']['test'])
    test = test_class(mem_map, directories, params)
    logger.info("Preparing before test %s", params['RunParameters']['test'])
    test.prepare_before_run()
    logger.info("Running test %s", params['RunParameters']['test'])
    test.run()
    logger.info("Cleaning after test %s", params['RunParameters']['test'])
    test.clean_after_run()
    logger.debug("Cleaning shared memory file")
    os.remove(params['General']['sharedMemFilePath'])
    mem_map.close()


if __name__ == '__main__':
    main()
