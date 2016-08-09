from time import time

from SDM.nodes.Datapath import Datapath
from SDM.rules.InPortRule import InPortRule
from SDM.util import *


class PushingDatapath(Datapath):
    def __init__(self, datapath, first_monitoring_table_id=1):
        super(PushingDatapath, self).__init__(datapath)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Created PushingDatapath")
        self.first_monitoring_table_id = first_monitoring_table_id

    def info(self, msg, *args, **kwargs):
        self.logger.info(str(time()) + " " + msg, *args, **kwargs)

    def calc_id(self):
        return 1

    def set_route_tables(self):
        for i in irange(1, 2):
            rule = InPortRule(self.datapath, 0, i, 1, None)
            actions = [self.datapath.ofproto_parser.OFPActionOutput(3 - i)]
            rule.add_flow_and_goto_next_table(actions)

    def set_main_monitor_table(self):
        assert False
        # In this part register the monitoring rules
        # For each rule, register the IP and subnet mask
        # and the created Match.
