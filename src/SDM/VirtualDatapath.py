from util import *
from src.SDM.InPortRule import InPortRule
from src.SDM.Datapath import Datapath

class VirtualDatapath(Datapath):
    def __init__(self, datapath):
        super(VirtualDatapath, self).__init__(datapath)

    def set_route_tables(self):
        for i in irange(1, 2):
            rule = InPortRule(self.datapath, 0, i, 0, None)
            actions = [self.datapath.ofproto_parser.OFPActionOutput(3 - i)]
            rule.add_flow_and_apply_actions(actions)

    def calc_id(self):
        """
        The id is not important for this type of datapath.
        """
        return -1