from src.SDM.BaseTest import BaseTest
from src.SDM.ThreeCycleTopo import ThreeCycleTopo


class MonitorTest(BaseTest):
    """
    A class that runs 3-cycle Topo with monitoring.
    """

    def __init__(self, shared_mem, directories, params):
        super(MonitorTest, self).__init__(shared_mem, directories, params)

    def run(self):
        super(MonitorTest, self).run()

    def setup_topo(self):
        self.topo = ThreeCycleTopo()
        return self.topo