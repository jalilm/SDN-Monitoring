import logging

from SDM.nodes.SynMiddleWare import SynMiddleWare
from SDM.rules.SynSrcPushingRule import SynSrcPushingRule


class SrcSynMiddleWare(SynMiddleWare):
    def __init__(self, ovs_switch, controller_ip="127.0.0.1", switch_ip=None, controller_port=6633, switch_port=None,
                 protocols=None):
        super(SrcSynMiddleWare, self).__init__(ovs_switch, controller_ip, switch_ip, controller_port, switch_port,
                                           protocols)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Created SrcSynMiddleWare")

    def create_rule(self, ip_addr, mask):
        return SynSrcPushingRule(self.ovs_switch, self.datapath, ip_addr, mask, 1, 2, None, self.protocol_str)
