from multiprocessing import Lock

from src.SDM.util import *
from src.SDM.InPortRule import InPortRule
from src.SDM.MainDatapath import MainDatapath
from src.pulling.FlagsDestRule import FlagsDestRule
from src.SDM.TCPIPDestRule import TCPIPDestRule


class SynDatapath(MainDatapath):
    def __init__(self, datapath):
        super(SynDatapath, self).__init__(datapath, first_monitoring_table_id=1)

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

    def request_stats(self):
        finished_last_round = self.received_all_replys()
        while not finished_last_round:
            finished_last_round = self.received_all_replys()

        self.round_status = {}
        self.frontier = self.next_frontier
        self.next_frontier = []

        for rule in self.frontier:
            req = self.datapath.ofproto_parser.OFPFlowStatsRequest(datapath=self.datapath,
                                                                   flags=0,
                                                                   table_id=rule.table_id,
                                                                   out_port=self.datapath.ofproto.OFPP_ANY,
                                                                   out_group=self.datapath.ofproto.OFPG_ANY,
                                                                   cookie=0,
                                                                   cookie_mask=0,
                                                                   match=rule.get_match())
            self.datapath.send_msg(req)

    def set_main_monitor_table(self):
        actions = []

        # In this part register the monitoring rules
        # For each rule, register the IP and subnet mask
        # and the created Match.

        ipv4_string = '39.128.128.0'
        subnet_string = CIDR_mask_to_ipv4_subnet_mask(24)

        rule = FlagsDestRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 1, 0x02, None)
        self.root_rules.append(rule)
        self.next_frontier.append(rule)
        self.frontier_locks[rule] = Lock()
        self.frontier_bw[rule] = 0

        rule = TCPIPDestRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 1, None)
        self.root_rules.append(rule)
        self.next_frontier.append(rule)
        self.frontier_locks[rule] = Lock()
        self.frontier_bw[rule] = 0

        # Till here

        for rule in self.next_frontier:
            rule.add_flow_and_goto_next_table(actions)
            self.round_status[rule] = 0
