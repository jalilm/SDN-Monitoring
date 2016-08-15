from ryu.ofproto import ether
from SDM.rules.Rule import Rule


class IPRule(Rule):
    """
    A class that represents an IP rule in the switch table.
    """

    def __init__(self, datapath, table_id=0, priority=0, father_rule=None):
        super(IPRule, self).__init__(datapath, table_id, priority, father_rule)
        self.add_match_arg('eth_type', ether.ETH_TYPE_IP)

    def __repr__(self):
        return "IPRule(" + repr(self.datapath) + ", " + repr(self.table_id) + \
               ", " + repr(self.priority) + ")"

    def __str__(self):
        return "IPRule"
