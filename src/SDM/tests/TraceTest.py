from time import sleep
from datetime import datetime
import logging

from src.SDM.nodes.RyuRemoteController import RyuRemoteController
from src.SDM.tests.BaseTest import BaseTest


class TraceTest(BaseTest):
    """
    A class that runs a single switch with 2 hosts, that
    sends previously captured traces.
    """

    def __init__(self, shared_mem, directories, params):
        super(TraceTest, self).__init__(shared_mem, directories, params)
        self.logger = logging.getLogger(__name__)

    def setup_net(self):
        self.logger.debug("setup_net")
        net = super(TraceTest, self).setup_net()
        net.addController(RyuRemoteController(name="c0", ip=self.params['General']['controllerIP'],
                                              port=self.params['General']['controllerPort'],
                                              ryuArgs=["",
                                                       self.params['RunParameters']['ryuApps']]))
        return net

    def run(self):
        """
        Executes the test and Mininet and the tcpreplay.
        """
        self.logger.info("run")
        if self.params['RunParameters']['interact']:
            self.net.build()
            self.net.interact()
            return

        self.logger.debug("starting the net")
        self.net.start()

        # delay used to allow completion of the handshake
        self.logger.debug("sleeping 30 sec to allow completion of the handshake")
        sleep(30)
        self.detect_alert()
        host1 = self.net.get('h1')
        if self.params['RunParameters']['before_attack'] != '':
            host1.cmd(self.params['RunParameters']['before_attack'])
        if self.params['RunParameters']['attack'] != '':
            self.logger.info(" - " + datetime.now().strftime('%H:%M:%S.%f') + " Attack started traces from h1")
            host1.cmd(self.params['RunParameters']['attack'])
            self.logger.info(" - " + datetime.now().strftime('%H:%M:%S.%f') + " Attack finished from h1")
        if self.params['RunParameters']['after_attack'] != '':
            host1.cmd(self.params['RunParameters']['after_attack'])
        self.logger.debug("Stopping the net")
        if str(self.shared_mem_fd[:6]) != self.params['General']['alertToken']:
            self.shared_mem_fd[:6] = self.params['General']['finishGenerationToken']
            sleep(self.params['RunParameters']['timeStep'] + 1)
            self.net.stop()
