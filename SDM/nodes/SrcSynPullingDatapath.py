import logging
from SDM.nodes.PullingDatapath import PullingDatapath
from SDM.rules.SynSrcRule import SynSrcRule
from SDM.util import CIDR_mask_to_ipv4_subnet_mask


class SrcSynPullingDatapath(PullingDatapath):
    def __init__(self, datapath, first_monitoring_table_id=1):
        super(SrcSynPullingDatapath, self).__init__(datapath, first_monitoring_table_id)
        self.frontier_default_value = {'tcp_packets': 0, 'syn_packets': 0}
        self.logger = logging.getLogger(__name__)
        self.logger.info("SrcSynPullingDatapath")

        # In this part register the monitoring rules
        # For each rule, register the IP and subnet mask
        # and the created Match.

        ipv4_string = '128.0.0.0'
        subnet_string = CIDR_mask_to_ipv4_subnet_mask(1)
        rule = SynSrcRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 2, None)
        self.add_monitoring_rule(rule)

        ipv4_string = '0.0.0.0'
        subnet_string = CIDR_mask_to_ipv4_subnet_mask(1)
        rule = SynSrcRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 2, None)
        self.add_monitoring_rule(rule)
