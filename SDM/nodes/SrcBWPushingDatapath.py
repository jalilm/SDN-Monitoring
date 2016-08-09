from SDM.nodes.PushingDatapath import PushingDatapath
from SDM.rules.IPSrcRule import IPSrcRule
from SDM.util import *


class SrcBWPushingDatapath(PushingDatapath):
    def __init__(self, datapath, first_monitoring_table_id=1):
        super(SrcBWPushingDatapath, self).__init__(datapath, first_monitoring_table_id)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Created SrcBWPushingDatapath")

    def set_main_monitor_table(self):
        actions = []

        # In this part register the monitoring rules
        # For each rule, register the IP and subnet mask
        # and the created Match.

        ipv4_string = '0.0.0.0'
        subnet_string = CIDR_mask_to_ipv4_subnet_mask(1)
        rule = IPSrcRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 0, None)
        rule.add_flow_and_goto_next_table(actions)

        ipv4_string = '128.0.0.0'
        subnet_string = CIDR_mask_to_ipv4_subnet_mask(1)
        rule = IPSrcRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 0, None)
        rule.add_flow_and_goto_next_table(actions)
        # Till here
