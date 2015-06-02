
import logging

from src.SDM.tests.TraceTest import TraceTest
from src.SDM.topologies.SynTraceTopo import SynTraceTopo



class SynTraceTest(TraceTest):
    """
    A class that runs a single switch with 2 hosts, that
    sends previously captured traces.
    """

    def __init__(self, shared_mem, directories, params):
        super(SynTraceTest, self).__init__(shared_mem, directories, params)
        self.logger = logging.getLogger(__name__)

    def setup_topo(self):
        self.logger.debug("setup_topo")
        return SynTraceTopo()

    def run(self):
        """
        Executes the test and Mininet and the tcpreplay.
        """
        self.logger.info("run")
        self.net.build()
        self.net.interact()
        return
