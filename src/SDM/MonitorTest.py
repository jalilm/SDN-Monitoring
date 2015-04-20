from src.SDM.BaseTest import BaseTest
from src.SDM.ThreeCycleTopo import ThreeCycleTopo
import logging

class MonitorTest(BaseTest):
    """
    A class that runs 3-cycle Topo with monitoring.
    """

    def __init__(self, shared_mem, directories, params):
        super(MonitorTest, self).__init__(shared_mem, directories, params)
        self.logger = logging.getLogger(__name__)

    def run(self):
        self.logger.debug("run")
        super(MonitorTest, self).run()

    def setup_topo(self):
        self.logger.debug("setup_topo")
        self.topo = ThreeCycleTopo()
        return self.topo