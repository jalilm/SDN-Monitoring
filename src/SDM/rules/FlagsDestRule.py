from src.SDM.rules.TCPIPDestRule import TCPIPDestRule


class FlagsDestRule(TCPIPDestRule):
    """
    A class that represents a rule based on destination IPV4 and mask and TCP flags
    """

    def __init__(self, datapath, ipv4_string, subnet_string, table_id=0, priority=0, tcp_flags=0x00, father_rule=None):
        super(FlagsDestRule, self).__init__(datapath, ipv4_string, subnet_string, table_id, priority, father_rule)
        self.add_match_arg('tcp_flags', tcp_flags)

    def __repr__(self):
        return "FlagsDestRule(" + repr(self.datapath) + ", " + repr(self.ipv4_string) + ", " \
               + ", " + repr(self.subnet_string) + ", " + repr(self.table_id) + ", " + repr(self.priority) + ", " + \
               repr(self.match_args['tcp_flags']) + ")"

    def __str__(self):
        return "FlagsDestRule ({self.ipv4_string}, {self.subnet_string}) Flags:{self.match_args['tcp_flags']}".format(
            self=self)

    # noinspection PyPep8Naming
    @classmethod
    def from_TCPIPDestRule(cls, rule, tcp_flags):
        return cls(rule.datapath, rule.ipv4_string, rule.subnet_string, rule.table_id, rule.priority, tcp_flags,
                   rule.father_rule)

    def get_paired_rule(self):
        return FlagsDestRule.from_TCPIPDestRule(super(FlagsDestRule, self).get_paired_rule(),
                                                self.match_args['tcp_flags'])

    def get_finer_rules(self):
        rules = []
        base_rules = super(FlagsDestRule, self).get_finer_rules()
        for base_rule in base_rules:
            rule = FlagsDestRule.from_TCPIPDestRule(base_rule, self.match_args['tcp_flags'])
            rules.append(rule)
            rules.append(rule.get_paired_rule())
        return rules
