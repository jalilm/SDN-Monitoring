from src.SDM.Rule import Rule


class InPortRule(Rule):
    """
    A class that represents a rule based on in_port
    """

    def __init__(self, datapath, table_id, in_port, priority, eth_dst=None):
        super(InPortRule, self).__init__(datapath, table_id, priority)
        self.in_port = in_port
        self.eth_dst = eth_dst
        if None == self.eth_dst:
            new_match = self.datapath.ofproto_parser.OFPMatch(in_port=in_port)
        else:
            new_match = self.datapath.ofproto_parser.OFPMatch(in_port=in_port, eth_dst=eth_dst)
        self.match = new_match