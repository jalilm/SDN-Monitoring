from SDM.nodes.PushingDatapath import PushingDatapath
from SDM.rules.SynDestRule import SynDestRule
from SDM.util import CIDR_mask_to_ipv4_subnet_mask


class SynPushingDatapath(PushingDatapath):
    def __init__(self, datapath, first_monitoring_table_id=1):
        super(SynPushingDatapath, self).__init__(datapath, first_monitoring_table_id)
        self.logger.debug("Created SynPushingDatapath")

    def set_main_monitor_table(self):
        actions = []

        # In this part register the monitoring rules
        # For each rule, register the IP and subnet mask
        # and the created Match.

        ipv4_string = '0.0.0.0'
        subnet_string = CIDR_mask_to_ipv4_subnet_mask(1)
        rule = SynDestRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 2, None)
        rule.add_flow_and_goto_next_table(actions)

        ipv4_string = '128.0.0.0'
        subnet_string = CIDR_mask_to_ipv4_subnet_mask(1)
        rule = SynDestRule(self.datapath, ipv4_string, subnet_string, self.first_monitoring_table_id, 2, None)
        rule.add_flow_and_goto_next_table(actions)
        # Till here
