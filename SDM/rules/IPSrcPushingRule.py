from SDM.rules.IPPushingRule import IPPushingRule
from SDM.util import get_index_of_least_sig_one, get_paired_ipv4, int_to_ipv4, ipv4_to_int


# noinspection PyAbstractClass
class IPSrcPushingRule(IPPushingRule):
    """
    A class that represents a rule based on source IPV4 and mask
    """

    def __init__(self, switch, datapath, ipv4_string, subnet_string, table_id=0, priority=0, father_rule=None,
                 protocol="OpenFlow13"):
        assert 4 == len(ipv4_string.split("."))
        assert 4 == len(subnet_string.split("."))
        super(IPSrcPushingRule, self).__init__(switch, datapath, table_id, priority, father_rule, protocol)

        self.ipv4_string = ipv4_string
        self.subnet_string = subnet_string
        self.ipv4_int = ipv4_to_int(ipv4_string)
        self.subnet_int = ipv4_to_int(subnet_string)

        self.add_match_arg('nw_src', self.ipv4_string + "/" + self.subnet_string)

    def __repr__(self):
        return "IPSrcPushingRule(" + repr(self.switch) + ", " + repr(self.datapath) + ", " + repr(
            self.ipv4_string) + ", " \
               + repr(self.subnet_string) + ", " + repr(self.table_id) + ", " + repr(self.priority) + ")"

    def __str__(self):
        return "IPSrcPushingRule ({self.ipv4_string}, {self.subnet_string})".format(self=self)

    def get_paired_rule(self):
        return IPSrcPushingRule(self.switch, self.datapath, get_paired_ipv4(self.ipv4_string, self.subnet_string),
                                self.subnet_string,
                                self.table_id, self.priority, self.father_rule, self.protocol)

    def get_finer_rules(self):
        rules = []
        ls1 = get_index_of_least_sig_one(self.subnet_string)
        tmp = "1".zfill(ls1 + 1)[::-1]
        xor_mask = int("0b" + tmp.zfill(32)[::-1], 2)
        new_subnet_mask = int_to_ipv4(self.subnet_int ^ xor_mask)
        #  table <-> prio change required.
        if self.params['RunParameters']['mechanism'] == "table":
            rule = IPSrcPushingRule(self.switch, self.datapath, self.ipv4_string, new_subnet_mask, self.table_id + 1,
                                    self.priority,
                                    self, self.protocol)
        elif self.params['RunParameters']['mechanism'] == "prio":
            rule = IPSrcPushingRule(self.switch, self.datapath, self.ipv4_string, new_subnet_mask, self.table_id,
                                    self.priority + 2,
                                    self, self.protocol)
        else:
            assert False
        rules.append(rule)
        rules.append(rule.get_paired_rule())
        return rules
