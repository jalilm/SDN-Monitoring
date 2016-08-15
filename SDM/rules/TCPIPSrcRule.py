from ryu.lib.packet.in_proto import IPPROTO_TCP

from SDM.rules.IPSrcRule import IPSrcRule


class TCPIPSrcRule(IPSrcRule):
    """
    A class that represents a rule based on source IPV4 and mask and it is TCP.
    """

    def __init__(self, datapath, ipv4_string, subnet_string, table_id=0, priority=0, father_rule=None):
        super(TCPIPSrcRule, self).__init__(datapath, ipv4_string, subnet_string, table_id, priority, father_rule)
        self.add_match_arg('ip_proto', IPPROTO_TCP)

    # noinspection PyPep8Naming
    @classmethod
    def from_IPSrcRule(cls, rule):
        return cls(rule.datapath, rule.ipv4_string, rule.subnet_string, rule.table_id, rule.priority, rule.father_rule)

    def __repr__(self):
        return "TCPIPSrcRule(" + repr(self.datapath) + ", " + repr(self.ipv4_string) + ", " \
               + repr(self.subnet_string) + ", " + repr(self.table_id) + ", " + repr(self.priority) + ")"

    def __str__(self):
        return "TCPIPSrcRule ({self.ipv4_string}, {self.subnet_string})".format(self=self)

    def get_paired_rule(self):
        return TCPIPSrcRule.from_IPSrcRule(super(TCPIPSrcRule, self).get_paired_rule())

    def get_finer_rules(self):
        rules = []
        base_rules = super(TCPIPSrcRule, self).get_finer_rules()
        for base_rule in base_rules:
            rule = TCPIPSrcRule.from_IPSrcRule(base_rule)
            rules.append(rule)
        return rules
