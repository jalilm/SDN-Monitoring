from SDM import IPRule
from SDM import get_index_of_least_sig_one
from SDM import get_paired_ipv4
from SDM import int_to_ipv4
from SDM import ipv4_to_int


class IPDestRule(IPRule):
    """
    A class that represents a rule based on destination IPV4 and mask
    """

    def __init__(self, datapath, ipv4_string, subnet_string, table_id=0, priority=0, father_rule=None):
        assert 4 == len(ipv4_string.split("."))
        assert 4 == len(subnet_string.split("."))
        super(IPDestRule, self).__init__(datapath, table_id, priority, father_rule)

        self.ipv4_string = ipv4_string
        self.subnet_string = subnet_string
        self.ipv4_int = ipv4_to_int(ipv4_string)
        self.subnet_int = ipv4_to_int(subnet_string)

        self.add_match_arg('ipv4_dst', (self.ipv4_int, self.subnet_int))

    def __repr__(self):
        return "IPDestRule(" + repr(self.datapath) + ", " + repr(self.ipv4_string) + ", " \
               + repr(self.subnet_string) + ", " + repr(self.table_id) + ", " + repr(self.priority) + ")"

    def __str__(self):
        return "IPDestRule ({self.ipv4_string}, {self.subnet_string})".format(self=self)

    def get_paired_rule(self):
        return IPDestRule(self.datapath, get_paired_ipv4(self.ipv4_string, self.subnet_string),
                          self.subnet_string,
                          self.table_id, self.priority, self.father_rule)

    def get_finer_rules(self):
        rules = []
        ls1 = get_index_of_least_sig_one(self.subnet_string)
        tmp = "1".zfill(ls1 + 1)[::-1]
        xor_mask = int("0b" + tmp.zfill(32)[::-1], 2)
        new_subnet_mask = int_to_ipv4(self.subnet_int ^ xor_mask)
        # TODO: table <-> prio change required.
        if self.params['RunParameters']['mechanism'] == "table":
            rule = IPDestRule(self.datapath, self.ipv4_string, new_subnet_mask, self.table_id+1, self.priority,
                          self)
        elif self.params['RunParameters']['mechanism'] == "prio":
            rule = IPDestRule(self.datapath, self.ipv4_string, new_subnet_mask, self.table_id, self.priority + 2,
                          self)
        else:
            assert False
        rules.append(rule)
        rules.append(rule.get_paired_rule())
        return rules
