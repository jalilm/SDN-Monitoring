from multiprocessing import Lock
import re

from util import *
from src.SDM.IPDestRule import IPDestRule
from src.SDM.Datapath import Datapath


class MainDatapath(Datapath):
    BASE_MAC = '6a:bc:af:76:'

    def __init__(self, datapath, first_monitoring_table_id):
        super(MainDatapath, self).__init__(datapath)
        self.first_monitoring_table_id = first_monitoring_table_id
        self.root_rules = []
        self.frontier = []
        self.next_frontier = []
        self.frontier_bw = {}
        self.frontier_locks = {}
        self.round_status = {}
        self.sibling_rule = {}

    def calc_id(self):
        self.mac_reg = re.compile(MainDatapath.BASE_MAC + '0(\d):(\d)(\d)')
        for port_id in self.datapath.ports:
            m = self.mac_reg.match(self.datapath.ports[port_id].hw_addr)
            if m.group(1) == m.group(2):
                return int(m.group(1))
        # Should not reach here, there must be a port that is "main" port.
        assert False


    def set_route_tables(self):
        """
        Set the routing tables needed for the simulation.
        """
        for port_id in self.datapath.ports:
            self.set_port_rules(port_id)

    def set_port_rules(self, port_id):
        m = self.mac_reg.match(self.datapath.ports[port_id].hw_addr)
        if m.group(1) == m.group(2):
            ipv4_string = '10.0.' + m.group(1) + '.' + m.group(3)
            subnet_string = '255.255.255.255'
        else:
            ipv4_string = '10.0.' + m.group(3) + '.0'
            subnet_string = '255.255.255.0'

        rule = IPDestRule(self.datapath, ipv4_string, subnet_string, 0, 0, None)
        actions = [self.datapath.ofproto_parser.OFPActionOutput(port_id)]
        rule.add_flow_and_goto_next_table(actions)

    def set_main_monitor_table(self):
        actions = []

        # In this part register the monitoring rules
        # For each rule, register the IP and subnet mask
        # and the created Match.

        ipv4_string = '10.0.' + str(self.id) + '.0'
        subnet_string = CIDR_mask_to_ipv4_subnet_mask(24)
        rule = IPDestRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 0, None)
        self.root_rules.append(rule)
        self.next_frontier.append(rule)
        self.frontier_locks[rule] = Lock()
        self.frontier_bw[rule] = 0

        # Till here

        for rule in self.next_frontier:
            rule.add_flow_and_goto_next_table(actions)
            self.round_status[rule] = True

    def received_all_replys(self):
        for rule in self.frontier:
            if not self.round_status.has_key(rule):
                return False
        return True

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
            self.round_status[rule] = None

    def increase_monitoring_level(self, rule):
        if rule.subnet_string == "255.255.255.255":
            self.next_frontier.append(self.get_original_rule(rule))
            return False  # Alert
        if rule not in self.frontier:
            print "rule is not in subrules - 1"
            assert False
        with self.frontier_locks[rule]:
            if rule not in self.frontier:
                print "rule is not in subrules - 2"
                assert False
            orig_rule = self.get_original_rule(rule)
            self.set_refined_monitoring_rules(orig_rule)
        return True

    def set_refined_monitoring_rules(self, rule):
        rules = rule.get_finer_rules()
        actions = []

        for r in rules:
            if r not in self.frontier:
                self.frontier_locks[r] = Lock()
                self.next_frontier.append(r)
                self.frontier_bw[r] = 0
                self.sibling_rule[r] = list(set(rules)- {r})
                r.add_flow_and_goto_next_table(actions)

        self.round_status[rule] = True

        #self.frontier.remove(rule)
        #self.frontier_bw.pop(rule, None)

    def reduce_monitoring_level(self, rule):
        orig_rule = self.get_original_rule(rule)
        if orig_rule in self.root_rules:
            self.next_frontier.append(orig_rule)
            return (False,"I'm root rule")
        if orig_rule not in self.frontier:
            print "rule is not in subrules - 3"
            assert False

        with self.frontier_locks[orig_rule]:
            self.round_status[orig_rule] = False

        return self.remove_refined_monitoring_rules(orig_rule)

    def remove_refined_monitoring_rules(self, rule):
        sibling = self.sibling_rule[rule][0]

        with self.frontier_locks[sibling]:
            if sibling not in self.frontier:
                self.next_frontier.append(rule)
                return (False, "waiting for bro children")
            if self.round_status[sibling]:
                self.next_frontier.append(rule)
                return (False, "staying with bro")
            if self.round_status[sibling] is None:
                self.next_frontier.append(rule)
                return (False, "waiting for bro")

        corase_rule = rule.get_coarse_rule()

        if corase_rule not in self.frontier:
            self.next_frontier.append(corase_rule)
            self.frontier_bw[corase_rule] = 0

        rule.remove_flow()
        sibling.remove_flow()
        assert sibling in self.next_frontier
        self.next_frontier.remove(sibling)
        self.frontier_bw.pop(rule, None)
        self.frontier_bw.pop(sibling, None)
        self.frontier_locks.pop(rule)
        self.frontier_locks.pop(sibling)
        return (True, rule, sibling)

    def keep_monitoring_level(self, rule):
        orig_rule = self.get_original_rule(rule)
        self.next_frontier.append(orig_rule)

    def get_original_rule(self, rule):
        for r in self.frontier:
            if r == rule:
                return r
        print "rule is not original"
        assert False