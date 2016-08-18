from SDM.util import irange
from SDM.nodes.Datapath import Datapath
from SDM.rules.InPortRule import InPortRule


class PushingDatapath(Datapath):
    def __init__(self, datapath, first_monitoring_table_id=1):
        super(PushingDatapath, self).__init__(datapath)
        self.logger.debug("Created PushingDatapath")
        self.first_monitoring_table_id = first_monitoring_table_id

    # noinspection PyMethodMayBeStatic
    def calc_id(self):
        return 1

    def set_route_tables(self):
        for i in irange(1, 2):
            rule = InPortRule(self.datapath, 0, i, 1, None)
            actions = [self.datapath.ofproto_parser.OFPActionOutput(3 - i)]
            rule.add_flow_and_goto_next_table(actions)

    # noinspection PyMethodMayBeStatic
    def set_main_monitor_table(self):
        raise NotImplementedError
        # In this part register the monitoring rules
        # For each rule, register the IP and subnet mask
        # and the created Match.
