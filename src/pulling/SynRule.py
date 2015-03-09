from src.SDM.Rule import Rule


class SynRule(Rule):

    def __init__(self, datapath, table_id, priority):
        super(SynRule, self).__init__(datapath, table_id, priority)
        self.match = self.datapath.ofproto_parser.OFPMatch()