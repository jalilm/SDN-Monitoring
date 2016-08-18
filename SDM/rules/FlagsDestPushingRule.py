from SDM.rules.TCPIPDestPushingRule import TCPIPDestPushingRule


# noinspection PyAbstractClass
class FlagsDestPushingRule(TCPIPDestPushingRule):
    """
    A class that represents a rule based on destination IPV4 and mask and TCP flags
    """

    def __init__(self, switch, datapath, ipv4_string, subnet_string, table_id=0, priority=0, tcp_flags=0x00,
                 father_rule=None, protocol="OpenFlow15"):
        super(FlagsDestPushingRule, self).__init__(switch, datapath, ipv4_string, subnet_string, table_id, priority,
                                                   father_rule, protocol)
        self.add_match_arg('tcp_flags', tcp_flags)

    def __repr__(self):
        return "FlagsDestPushingRule(" + repr(self.datapath) + ", " + repr(self.ipv4_string) + ", " \
               + repr(self.subnet_string) + ", " + repr(self.table_id) + ", " + repr(self.priority) + ", " + \
               repr(self.match_args['tcp_flags']) + ")"

    def __str__(self):
        return "FlagsDestPushingRule ({self.ipv4_string}, {self.subnet_string}) Flags:{self.match_args[tcp_flags]}".\
            format(self=self)

    # noinspection PyPep8Naming
    @classmethod
    def from_TCPIPDestPushingRule(cls, rule, tcp_flags):
        return cls(rule.switch, rule.datapath, rule.ipv4_string, rule.subnet_string, rule.table_id, rule.priority,
                   tcp_flags, rule.father_rule, rule.protocol)

    def get_paired_rule(self):
        return FlagsDestPushingRule.from_TCPIPDestPushingRule(super(FlagsDestPushingRule, self).get_paired_rule(),
                                                              self.match_args['tcp_flags'])

    def get_finer_rules(self):
        rules = []
        base_rules = super(FlagsDestPushingRule, self).get_finer_rules()
        for base_rule in base_rules:
            rule = FlagsDestPushingRule.from_TCPIPDestPushingRule(base_rule, self.match_args['tcp_flags'])
            rules.append(rule)
        return rules
