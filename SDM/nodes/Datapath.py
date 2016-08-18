import logging
import re

from SDM.rules.IPDestRule import IPDestRule


class Datapath(object):
    BASE_MAC = '6a:bc:af:76:'

    def __init__(self, datapath):
        self.logger = logging.getLogger()
        # The order here is important
        self.datapath = datapath
        self.id = self.calc_id()
        self.mac_reg = re.compile(Datapath.BASE_MAC + '0(\d):(\d)(\d)')

    def calc_id(self):
        for port_id in self.datapath.ports:
            m = self.mac_reg.match(self.datapath.ports[port_id].hw_addr)
            if m.group(1) == m.group(2):
                return int(m.group(1))
        # Should not reach here, there must be a port that is "main" port.
        assert False

    def set_route_tables(self):
        """
        Set the routing tables needed for the simulation.
        """
        for port_id in self.datapath.ports:
            self.set_port_rules(port_id)

    def set_port_rules(self, port_id):
        m = self.mac_reg.match(self.datapath.ports[port_id].hw_addr)
        if m.group(1) == m.group(2):
            ipv4_string = '10.0.' + m.group(1) + '.' + m.group(3)
            subnet_string = '255.255.255.255'
        else:
            ipv4_string = '10.0.' + m.group(3) + '.0'
            subnet_string = '255.255.255.0'

        rule = IPDestRule(self.datapath, ipv4_string, subnet_string, 0, 0, None)
        actions = [self.datapath.ofproto_parser.OFPActionOutput(port_id)]
        rule.add_flow_and_goto_next_table(actions)
