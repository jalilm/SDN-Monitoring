import time

from src.SDM.BaseTest import BaseTest
from src.SDM.TraceTopo import TraceTopo
from src.pulling.RyuRemoteController import RyuRemoteController


class TraceTest(BaseTest):
    """
    A class that runs a single switch with 2 hosts, that
    sends previously captured traces.
    """

    def __init__(self, shared_mem, directories, params):
        super(TraceTest, self).__init__(shared_mem, directories, params)

    def setup_topo(self):
        self.topo = TraceTopo()
        return self.topo

    def setup_net(self):
        super(TraceTest, self).setup_net()
        self.net.addController(RyuRemoteController(name="c0", ip=self.params['General']['controllerIP'],
                                                   port=self.params['General']['controllerPort'],
                                                   ryuArgs=["",
                                                            "~/SDN-Monitoring/src/pulling/TracePullingController.py"]))
        return self.net

    def run(self):
        """
        Executes the test and Mininet and the tcpreplay.
        """
        #self.net.build()
        #self.net.interact()
        #return
        self.net.start()

        # TODO: delay used to allow completion of the handshake,
        # check if we can get rid of it.
        time.sleep(10)

        host1 = self.net.get('h1')
        # TODO: Sending 5 minutes data - Fix me!
        host1.cmd('bash ~/SDN-Monitoring/client')
        self.net.stop()
