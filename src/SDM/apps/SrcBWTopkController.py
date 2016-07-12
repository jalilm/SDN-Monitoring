from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from src.SDM.rules.IPSrcRule import IPSrcRule
from src.SDM.apps.SrcBWPullingController import SrcBWPullingController
import math

class SrcBWTopkController(SrcBWPullingController):
    def __init__(self, *args, **kwargs):
        super(SrcBWTopkController, self).__init__(*args, **kwargs)
        assert (math.log(self.parameters['RunParameters']['k'], 2)%1 == 0)

    def handle_rule_stat(self, rule, current_stat, main_datapath):
        main_datapath.handle_rule(rule, current_stat)
