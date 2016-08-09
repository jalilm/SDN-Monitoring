from SDM.rules.PushingRule import PushingRule


class IPPushingRule(PushingRule):
    """
    A class that represents an IP rule in the switch table.
    """

    def __init__(self, switch, datapath, table_id=0, priority=0, father_rule=None, protocol="OpenFlow13"):
        super(IPPushingRule, self).__init__(switch, datapath, table_id, priority, father_rule, protocol)
        self.add_match_arg('ip', None)

    def __repr__(self):
        return "IPPushingRule(" + repr(self.switch) + ", " + repr(self.datapath) + ", " + repr(self.table_id) + \
               ", " + repr(self.priority) + ")"

    def __str__(self):
        return "IPPushingRule"
