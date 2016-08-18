from SDM.rules.IPSrcPushingRule import IPSrcPushingRule


# noinspection PyAbstractClass
class TCPIPSrcPushingRule(IPSrcPushingRule):
    """
    A class that represents a rule based on Srcination IPV4 and mask
    """

    def __init__(self, switch, datapath, ipv4_string, subnet_string, table_id=0, priority=0, father_rule=None,
                 protocol="OpenFlow13"):
        super(TCPIPSrcPushingRule, self).__init__(switch, datapath, ipv4_string, subnet_string, table_id, priority,
                                                  father_rule, protocol)
        self.add_match_arg('tcp', None)

    def __repr__(self):
        return "TCPIPSrcPushingRule(" + repr(self.switch) + ", " + repr(self.datapath) + ", " + repr(
            self.ipv4_string) + ", " \
               + repr(self.subnet_string) + ", " + repr(self.table_id) + ", " + repr(self.priority) + ")"

    def __str__(self):
        return "TCPIPSrcPushingRule ({self.ipv4_string}, {self.subnet_string})".format(self=self)

    # noinspection PyPep8Naming
    @classmethod
    def from_IPSrcPushingRule(cls, rule):
        return cls(rule.switch, rule.datapath, rule.ipv4_string, rule.subnet_string, rule.table_id, rule.priority,
                   rule.father_rule, rule.protocol)

    def get_paired_rule(self):
        return TCPIPSrcPushingRule.from_IPSrcPushingRule(super(TCPIPSrcPushingRule, self).get_paired_rule())

    def get_finer_rules(self):
        rules = []
        base_rules = super(TCPIPSrcPushingRule, self).get_finer_rules()
        for base_rule in base_rules:
            rule = TCPIPSrcPushingRule.from_IPSrcPushingRule(base_rule)
            rules.append(rule)
        return rules
