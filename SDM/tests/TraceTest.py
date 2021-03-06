import logging
from datetime import datetime
from time import sleep

from SDM.tests.BaseTest import BaseTest
from SDM.nodes.RyuRemoteController import RyuRemoteController


class TraceTest(BaseTest):
    """
    A class that runs a single switch with 2 hosts, that
    sends previously captured traces.
    """

    def __init__(self, shared_mem, directories, parameters):
        super(TraceTest, self).__init__(shared_mem, directories, parameters)
        self.logger = logging.getLogger(__name__)

    def setup_net(self):
        self.logger.debug("setup_net")
        net = super(TraceTest, self).setup_net()
        net.addController(RyuRemoteController(name="c0", ip=self.parameters['General']['controllerIP'],
                                              port=self.parameters['General']['controllerPort'],
                                              ryuArgs=["", self.parameters['RunParameters']['ryuApps']]))
        return net

    def run(self):
        """
        Executes the test and Mininet and the tcpreplay.
        """
        self.logger.info("run")
        if self.parameters['RunParameters']['interact']:
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
        if self.parameters['RunParameters']['before_attack'] != '':
            host1.cmd(self.parameters['RunParameters']['before_attack'])
        if self.parameters['RunParameters']['attack'] != '':
            self.logger.info(" - " + datetime.now().strftime('%H:%M:%S.%f') + " Attack started traces from h1")
            host1.cmd(self.parameters['RunParameters']['attack'])
            self.logger.info(" - " + datetime.now().strftime('%H:%M:%S.%f') + " Attack finished from h1")
        if self.parameters['RunParameters']['after_attack'] != '':
            host1.cmd(self.parameters['RunParameters']['after_attack'])
        self.logger.debug("Stopping the net")
        if str(self.shared_mem_fd[:6]) != self.parameters['General']['alertToken']:
            self.shared_mem_fd[:6] = self.parameters['General']['finishGenerationToken']
            sleep(self.parameters['RunParameters']['timeStep'] + 1)
            self.net.stop()
