from multiprocessing import Lock

from src.SDM.nodes.TraceDatapath import TraceDatapath
from src.SDM.rules.IPSrcRule import IPSrcRule
from src.SDM.util import *
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.controller import ofp_event


class SrcTraceDatapath(TraceDatapath):
    def __init__(self, datapath):
        super(SrcTraceDatapath, self).__init__(datapath)
        self.datapaths = {}

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, CONFIG_DISPATCHER)
    def multipart_reply_handler(self, ev):
        datapath = ev.msg.datapath
        # if len(datapath.ports) == 2:
        # For OVS there is a down local port.
        if len(datapath.ports) == 3:
            self.datapaths[datapath] = SrcTraceDatapath(datapath)
            self.datapaths[datapath].set_route_tables()
            self.datapaths[datapath].set_main_monitor_table()
        else:
            assert False

    def set_main_monitor_table(self):
        actions = []

        # In this part register the monitoring rules
        # For each rule, register the IP and subnet mask
        # and the created Match.

        ipv4_string = '0.0.0.0'
        subnet_string = CIDR_mask_to_ipv4_subnet_mask(1)
        rule = IPSrcRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 0, None)
        self.root_rules.append(rule)
        self.next_frontier.append(rule)
        self.frontier_locks[rule] = Lock()
        self.frontier_values[rule] = 0

        ipv4_string = '128.0.0.0'
        subnet_string = CIDR_mask_to_ipv4_subnet_mask(1)
        rule = IPSrcRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 0, None)
        self.root_rules.append(rule)
        self.next_frontier.append(rule)
        self.frontier_locks[rule] = Lock()
        self.frontier_values[rule] = 0
        # Till here

        for rule in self.next_frontier:
            rule.add_flow_and_goto_next_table(actions)
            self.round_status[rule] = 0
