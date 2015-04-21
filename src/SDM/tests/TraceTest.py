import time
import logging

from src.SDM.nodes.RyuRemoteController import RyuRemoteController

from src.SDM.tests.BaseTest import BaseTest
from src.SDM.topologies.TraceTopo import TraceTopo


class TraceTest(BaseTest):
    """
    A class that runs a single switch with 2 hosts, that
    sends previously captured traces.
    """

    def __init__(self, shared_mem, directories, params):
        super(TraceTest, self).__init__(shared_mem, directories, params)
        self.logger = logging.getLogger(__name__)

    def setup_topo(self):
        self.logger.debug("setup_topo")
        return TraceTopo()

    def setup_net(self):
        self.logger.debug("setup_net")
        net = super(TraceTest, self).setup_net()
        net.addController(RyuRemoteController(name="c0", ip=self.params['General']['controllerIP'],
                                              port=self.params['General']['controllerPort'],
                                              ryuArgs=["",
                                                       self.params['RunParameters']['ryuApps']]))
                                                # "~/SDN-Monitoring/src/pulling/TracePullingController.py"]))
        return net

    def run(self):
        """
        Executes the test and Mininet and the tcpreplay.
        """
        self.logger.info("run")
        # self.net.build()
        # self.net.interact()
        # return
        self.logger.debug("starting the net")
        self.net.start()

        # TODO: delay used to allow completion of the handshake,
        # check if we can get rid of it.
        self.logger.debug("sleeping got 10 sec")
        time.sleep(10)

        host1 = self.net.get('h1')
        # TODO: Sending 5 minutes data - Fix me!
        self.logger.debug("running client on h1")
        host1.cmd('bash ~/SDN-Monitoring/client')
        self.logger.debug("Stopping the net")
        self.net.stop()
