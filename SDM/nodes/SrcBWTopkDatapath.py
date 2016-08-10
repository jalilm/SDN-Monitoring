import logging
import math

from SDM import Datapath
from SDM import IPSrcRule
from SDM import InPortRule
from SDM import TopkStrategy


class SrcBWTopkDatapath(TopkStrategy, Datapath):
    def __init__(self, datapath, first_monitoring_table_id=1):
        self.dirs = get_dirs()
        self.parameters = get_params(self.dirs)
        Datapath.__init__(self, datapath)
        TopkStrategy.__init__(self, self.parameters['RunParameters']['k'], self.parameters['RunParameters']['counters'],
                              first_monitoring_table_id)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("SrcBWTopkDatapath")

        # In this part register the monitoring rules
        # For each rule, register the IP and subnet mask
        # and the created Match.)
        ips = ipv4_partition(self.parameters['RunParameters']['counters'])

        for ipv4_string in ips:
            subnet_string = CIDR_mask_to_ipv4_subnet_mask(
                int(math.log(self.parameters['RunParameters']['counters'], 2)))
            rule = IPSrcRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 0, None)
            self.add_monitoring_rule(rule)

    def calc_id(self):
        """
        This type does not need id calculation.
        :return: 1 always
        """
        return 1

    def set_route_tables(self):
        for i in irange(1, 2):
            rule = InPortRule(self.datapath, 0, i, 1, None)
            actions = [self.datapath.ofproto_parser.OFPActionOutput(3 - i)]
            rule.add_flow_and_goto_next_table(actions)

    def request_stats(self):
        finished_last_round = self.received_all_replys()
        while not finished_last_round:
            self.warn("XXX requesting stats while last epoch stats are not ready yet!")
            finished_last_round = self.received_all_replys()

        if self.alert:
            return

        self.round_status = {}
        self.frontier = self.next_frontier
        self.logger.debug("Frontier is %s", self.frontier)
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
