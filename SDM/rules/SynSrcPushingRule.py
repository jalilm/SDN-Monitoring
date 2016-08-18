from SDM.rules.FlagsSrcPushingRule import FlagsSrcPushingRule
from SDM.rules.PushingRule import PushingRule
from SDM.rules.TCPIPSrcPushingRule import TCPIPSrcPushingRule


# noinspection PyAbstractClass
class SynSrcPushingRule(PushingRule):
    """
    A class that represents a rule in the switch table.
    """

    def __init__(self, switch, datapath, ipv4_string, subnet_string, table_id=0, priority=0, father_rule=None,
                 protocol="OpenFlow15"):
        super(SynSrcPushingRule, self).__init__(switch, datapath, table_id, priority, father_rule, protocol)
        self.ipv4_string = ipv4_string
        self.subnet_string = subnet_string
        self.tcp_rule = TCPIPSrcPushingRule(switch, datapath, ipv4_string, subnet_string, table_id, priority, None,
                                            protocol)
        self.syn_rule = FlagsSrcPushingRule(switch, datapath, ipv4_string, subnet_string, table_id, priority + 1, 0x02,
                                            None, protocol)
        self.match_args = self.tcp_rule.match_args
        self.match = self.tcp_rule.match

    def __repr__(self):
        return "SynSrcPushingRule(" + repr(self.datapath) + ", " + repr(self.tcp_rule.ipv4_string) + ", " \
               + repr(self.tcp_rule.subnet_string) + ", " + repr(self.table_id) + ", " + repr(
            self.priority) + ", " + \
               repr(self.syn_rule.match_args['tcp_flags']) + ")"

    def __str__(self):
        return "SynSrcPushingRule ({self.tcp_rule.ipv4_string}, {self.tcp_rule.subnet_string}) " \
               "Flags:{self.syn_rule.match_args[tcp_flags]}".format(self=self)

    def get_finer_rules(self):
        rules = []
        tcp_finer_rules = self.tcp_rule.get_finer_rules()
        syn_finer_rules = self.syn_rule.get_finer_rules()
        for t_rule in tcp_finer_rules:
            s_rule = [s_rule for s_rule in syn_finer_rules if
                      s_rule.ipv4_string == t_rule.ipv4_string and s_rule.subnet_string == t_rule.subnet_string][0]
            rule = SynSrcPushingRule.from_sub_rules(t_rule, s_rule, self)
            rules.append(rule)
        return rules

    def get_paired_rule(self):
        t_paired = self.tcp_rule.get_paired_rule()
        s_paired = self.syn_rule.get_paired_rule()
        return SynSrcPushingRule.from_sub_rules(t_paired, s_paired, self)

    def remove_flow(self):
        self.syn_rule.remove_flow()
        self.tcp_rule.remove_flow()

    def add_flow(self, inst):
        self.syn_rule.add_flow(inst)
        self.tcp_rule.add_flow(inst)

    # noinspection PyPep8Naming
    @classmethod
    def from_sub_rules(cls, tcp_rule, syn_rule, father_rule):
        r = cls(tcp_rule.switch, tcp_rule.datapath, tcp_rule.ipv4_string, tcp_rule.subnet_string, tcp_rule.table_id,
                tcp_rule.priority, father_rule, tcp_rule.protocol)
        r.tcp_rule = tcp_rule
        r.syn_rule = syn_rule
        return r
