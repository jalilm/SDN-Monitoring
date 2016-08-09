from SDM.nodes.PullingDatapath import PullingDatapath

from SDM.rules.IPDestRule import IPDestRule
from SDM.util import *


class BWPullingDatapath(PullingDatapath):
    def __init__(self, datapath, first_monitoring_table_id=1):
        super(BWPullingDatapath, self).__init__(datapath, first_monitoring_table_id)
        self.frontier_default_value = {'duration': 0.0, 'byte_count': 0}
        self.logger = logging.getLogger(__name__)
        self.logger.info("BWPullingDatapath")

        # In this part register the monitoring rules
        # For each rule, register the IP and subnet mask
        # and the created Match.

        ipv4_string = '0.0.0.0'
        subnet_string = CIDR_mask_to_ipv4_subnet_mask(1)
        rule = IPDestRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 0, None)
        self.add_monitoring_rule(rule)

        ipv4_string = '128.0.0.0'
        subnet_string = CIDR_mask_to_ipv4_subnet_mask(1)
        rule = IPDestRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 0, None)
        self.add_monitoring_rule(rule)
