from src.SDM.util import get_index_of_least_sig_one
from src.SDM.util import ipv4_to_int
from src.SDM.util import int_to_ipv4
from src.SDM.util import get_paired_ipv4
from ryu.ofproto import ether
from src.SDM.Rule import Rule


class IPv4DestinationRule(Rule):
    """
    A class that represents a rule based on destination IPV4 and mask
    """

    def __init__(self, datapath, ipv4_string, subnet_string, table_id, priority, father_rule):
        assert 4 == len(ipv4_string.split("."))
        assert 4 == len(subnet_string.split("."))
        super(IPv4DestinationRule, self).__init__(datapath, table_id, priority)

        self.ipv4_string = ipv4_string
        self.subnet_string = subnet_string
        self.ipv4_int = ipv4_to_int(ipv4_string)
        self.subnet_int = ipv4_to_int(subnet_string)
        self.father_rule = father_rule

        new_match = datapath.ofproto_parser.OFPMatch()
        new_match.set_dl_type(ether.ETH_TYPE_IP)
        if self.subnet_string == "255.255.255.255":
            new_match.set_ipv4_dst(self.ipv4_int)
        else:
            new_match.set_ipv4_dst_masked(self.ipv4_int, self.subnet_int)
        new_match.tcp_flags = 0
        self.match = new_match

    def __str__(self):
        return "(" + self.ipv4_string + ", " + self.subnet_string + ")"

    def __hash__(self):
        """
        Hash value according to immutable ipv4_string and subnet_string.
        :return: hash value.
        """
        return self.__str__().__hash__()

    def __eq__(self, other):
        """
        Two destination rules are equal, if and only if the ipv4 and subnet masks are equal.
        :param other: The other rule to be compared.
        :return: True if and only if they are equal.
        """
        return isinstance(other, IPv4DestinationRule) and self.__hash__() == other.__hash__()

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_match(self):
        copy_match = self.datapath.ofproto_parser.OFPMatch()
        copy_match.set_dl_type(self.match._flow.dl_type)
        copy_match.set_ipv4_dst_masked(self.match._flow.ipv4_dst, self.match._wc.ipv4_dst_mask)
        return copy_match

    def get_paired_rule(self):
        return IPv4DestinationRule(self.datapath, get_paired_ipv4(self.ipv4_string, self.subnet_string),
                                   self.subnet_string,
                                   self.table_id, self.priority, self.father_rule)

    def get_finer_rules(self):
        rules = []
        ls1 = get_index_of_least_sig_one(self.subnet_string)
        tmp = "1".zfill(ls1 + 1)[::-1]
        xor_mask = int("0b" + tmp.zfill(32)[::-1], 2)
        new_subnet_mask = int_to_ipv4(self.subnet_int ^ xor_mask)
        rule = IPv4DestinationRule(self.datapath, self.ipv4_string, new_subnet_mask, self.table_id + 1, self.priority,
                                   self)
        rules.append(rule)
        rules.append(rule.get_paired_rule())
        return rules

    def get_coarse_rule(self):
        return self.father_rule