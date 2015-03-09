import os
import time
from subprocess import Popen

from src.SDM.util import irange
from src.SDM.BaseTest import BaseTest


class NormalTest(BaseTest):
    """
    A class that runs the normal test.
    """

    def __init__(self, shared_mem, directories, params):
        super(NormalTest, self).__init__(shared_mem, directories, params)

    def merge_logs(self):
        """
        Calls a bash script to clean up and summarize the logs.
        """
        curr_dir = os.getcwd()
        os.chdir(self.directories['log'])
        Popen(self.directories['util'] + 'mergeLogs ' +
              str(self.params['RunParameters']['numberOfStations']), shell=True)
        os.chdir(curr_dir)

    def run(self):
        """
        Executes the test and Mininet and the On-Off traffic model of the hosts
        """
        #self.net.build()
        self.net.start()

        # TODO: delay used to allow completion of the handshake,
        # check if we can get rid of it.
        time.sleep(10)

        #self.net.interact()
        #self.net.get('h1').cmd(self.directories['src'] + 'MultiThreadServer.py 1 &')
        #self.net.get('h2').cmd(self.directories['src'] + 'MultiThreadClient.py 2 2')
        #return

        for i in irange(1, self.params['RunParameters']['numberOfStations']):
            hosti = self.net.get('h' + str(i))
            hosti.cmd(self.directories['src'] + 'MultiThreadServer.py ' +
                      str(i) + ' &')

        for i in irange(1, self.params['RunParameters']['numberOfStations']):
            hosti = self.net.get('h' + str(i))
            hosti.sendCmd(self.directories['src'] + 'MultiThreadClient.py ' +
                          str(i) + ' ' +
                          str(self.params['RunParameters']['numberOfStations']))

        for i in irange(1, self.params['RunParameters']['numberOfStations']):
            hosti = self.net.get('h' + str(i))
            hosti.waitOutput()

        # TODO: fix that the finish token should be same length as start token
        self.shared_mem_fd[0:] = self.params['General']['finishGenerationToken']
        self.net.stop()
