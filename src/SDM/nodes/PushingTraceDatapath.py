from multiprocessing import Lock

from src.SDM.nodes.MainDatapath import MainDatapath
from src.SDM.rules.IPDestRule import IPDestRule
from src.SDM.util import *
from src.SDM.rules.InPortRule import InPortRule


class PushingTraceDatapath(MainDatapath):
    def __init__(self, datapath):
        super(PushingTraceDatapath, self).__init__(datapath, first_monitoring_table_id=1)

    def set_route_tables(self):
        for i in irange(1, 2):
            # TODO: jalil - prio was change from 0 to 1
            # rule = InPortRule(self.datapath, 0, i, 0, None)
            rule = InPortRule(self.datapath, 0, i, 1, None)
            actions = [self.datapath.ofproto_parser.OFPActionOutput(3 - i)]
            rule.add_flow_and_goto_next_table(actions)

    def calc_id(self):
        """
        This type does not need id calculation.
        :return: 1 always
        """
        return 1

    def set_main_monitor_table(self):
        actions = []

        # In this part register the monitoring rules
        # For each rule, register the IP and subnet mask
        # and the created Match.

        ipv4_string = '0.0.0.0'
        subnet_string = CIDR_mask_to_ipv4_subnet_mask(1)
        rule = IPDestRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 0, None)
        self.root_rules.append(rule)
        self.next_frontier.append(rule)
        self.frontier_locks[rule] = Lock()
        self.frontier_values[rule] = 0

        ipv4_string = '128.0.0.0'
        subnet_string = CIDR_mask_to_ipv4_subnet_mask(1)
        rule = IPDestRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 0, None)
        self.root_rules.append(rule)
        self.next_frontier.append(rule)
        self.frontier_locks[rule] = Lock()
        self.frontier_values[rule] = 0
        # Till here

        for rule in self.next_frontier:
            rule.add_flow_and_goto_next_table(actions)
            self.round_status[rule] = 0

