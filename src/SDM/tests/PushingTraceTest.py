
import logging

from src.SDM.tests.TraceTest import TraceTest
from src.SDM.nodes.PushingSwitch import PushingSwitch



class PushingTraceTest(TraceTest):

    def __init__(self, shared_mem, directories, params):
        super(PushingTraceTest, self).__init__(shared_mem, directories, params)
        self.logger = logging.getLogger(__name__)

    def setup_net(self, switch=PushingSwitch):
        self.logger.debug("setup_net")
        return super(PushingTraceTest, self).setup_net(switch)

    def run(self):
        """
        Executes the test and Mininet and the tcpreplay.
        """
        self.logger.info("run")
        self.net.build()
        self.net.interact()
        return
