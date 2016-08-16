import logging

from SDM.nodes.BWMiddleWare import BWMiddleWare
from SDM.rules.IPSrcPushingRule import IPSrcPushingRule


class SrcBWMiddleWare(BWMiddleWare):
    def __init__(self, ovs_switch, controller_ip="127.0.0.1", switch_ip=None, controller_port=6633, switch_port=None,
                 protocols=None):
        super(SrcBWMiddleWare, self).__init__(ovs_switch, controller_ip, switch_ip, controller_port, switch_port,
                                              protocols)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Created SrcBWMiddleWare")

    def create_rule(self, ip_addr, mask):
        return IPSrcPushingRule(self.ovs_switch, self.datapath, ip_addr, mask, 1, 0, None, self.protocol_str)
