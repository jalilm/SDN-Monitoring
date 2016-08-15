import logging
import os
import time
from subprocess import Popen

from SDM.tests.BaseTest import BaseTest
from SDM.util import irange


class NormalTest(BaseTest):
    """
    A class that runs the normal test.
    """

    def __init__(self, shared_mem, directories, parameters):
        super(NormalTest, self).__init__(shared_mem, directories, parameters)
        self.logger = logging.getLogger(__name__)

    def clean_after_run(self):
        """
        Calls a bash script to clean up and summarize the logs.
        """
        self.logger.debug("clean_after_run")
        curr_dir = os.getcwd()
        os.chdir(self.directories['log'])
        Popen(self.directories['util'] + 'mergeLogs ' +
              str(self.parameters['RunParameters']['numberOfStations']), shell=True)
        os.chdir(curr_dir)

    def run(self):
        """
        Executes the test and Mininet and the On-Off traffic model of the hosts
        """
        self.logger.info("run")
        self.logger.debug("starting the net")
        self.net.start()

        # delay used to allow completion of the handshake,
        self.logger.debug("sleeping for 10 sec")
        time.sleep(10)

        self.logger.debug("running MultiThreadServer on the hosts")
        for i in irange(1, self.parameters['RunParameters']['numberOfStations']):
            hosti = self.net.get('h' + str(i))
            hosti.cmd(self.directories['src'] + 'scripts/MultiThreadServer.py ' +
                      str(i) + ' &')

        self.logger.debug("running MultiThreadClient on the hosts")
        for i in irange(1, self.parameters['RunParameters']['numberOfStations']):
            hosti = self.net.get('h' + str(i))
            hosti.sendCmd(self.directories['src'] + 'scripts/MultiThreadClient.py ' +
                          str(i) + ' ' +
                          str(self.parameters['RunParameters']['numberOfStations']))

        self.logger.debug("waiting for the hosts")
        for i in irange(1, self.parameters['RunParameters']['numberOfStations']):
            hosti = self.net.get('h' + str(i))
            hosti.waitOutput()

        self.shared_mem_fd[0:] = self.parameters['General']['finishGenerationToken']
        self.logger.debug("stopping the net")
        self.net.stop()
