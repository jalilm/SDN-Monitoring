from src.SDM.rules.IPDestPushingRule import IPDestPushingRule


class TCPIPDestPushingRule(IPDestPushingRule):
    """
    A class that represents a rule based on destination IPV4 and mask
    """

    def __init__(self, switch, datapath, ipv4_string, subnet_string, table_id=0, priority=0, father_rule=None,
                 protocol="OpenFlow13"):
        super(TCPIPDestPushingRule, self).__init__(switch, datapath, ipv4_string, subnet_string, table_id, priority,
                                                   father_rule, protocol)
        self.add_match_arg('tcp', None)

    def __repr__(self):
        return "TCPIPDestPushingRule(" + repr(self.switch) + ", " + repr(self.datapath) + ", " + repr(
            self.ipv4_string) + ", " \
               + repr(self.subnet_string) + ", " + repr(self.table_id) + ", " + repr(self.priority) + ")"

    def __str__(self):
        return "TCPIPDestPushingRule ({self.ipv4_string}, {self.subnet_string})".format(self=self)

    # noinspection PyPep8Naming
    @classmethod
    def from_IPDestPushingRule(cls, rule):
        return cls(rule.switch, rule.datapath, rule.ipv4_string, rule.subnet_string, rule.table_id, rule.priority,
                   rule.father_rule, rule.protocol)

    def get_paired_rule(self):
        return TCPIPDestPushingRule.from_IPDestPushingRule(super(TCPIPDestPushingRule, self).get_paired_rule())

    def get_finer_rules(self):
        rules = []
        base_rules = super(TCPIPDestPushingRule, self).get_finer_rules()
        for base_rule in base_rules:
            rule = TCPIPDestPushingRule.from_IPDestPushingRule(base_rule)
            rules.append(rule)
        return rules
