from src.SDM.nodes.Datapath import Datapath
from src.SDM.nodes.Strategy import Strategy
from src.SDM.util import *
from src.SDM.rules.InPortRule import InPortRule


class PullingDatapath(Datapath, Strategy):
    def __init__(self, datapath, first_monitoring_table_id=1):
        Datapath.__init__(self, datapath)
        Strategy.__init__(self, first_monitoring_table_id)
        self.logger = logging.getLogger(__name__)
        self.logger.info("PullingDatapath")

    def calc_id(self):
        """
        This type does not need id calculation.
        :return: 1 always
        """
        return 1

    def set_route_tables(self):
        for i in irange(1, 2):
            rule = InPortRule(self.datapath, 0, i, 1, None)
            actions = [self.datapath.ofproto_parser.OFPActionOutput(3 - i)]
            rule.add_flow_and_goto_next_table(actions)

    def request_stats(self):
        finished_last_round = self.received_all_replys()
        while not finished_last_round:
            finished_last_round = self.received_all_replys()

        self.round_status = {}
        self.frontier = self.next_frontier
        self.next_frontier = []

        for rule in self.frontier:
            req = self.datapath.ofproto_parser.OFPFlowStatsRequest(datapath=self.datapath,
                                                                   flags=0,
                                                                   table_id=rule.table_id,
                                                                   out_port=self.datapath.ofproto.OFPP_ANY,
                                                                   out_group=self.datapath.ofproto.OFPG_ANY,
                                                                   cookie=0,
                                                                   cookie_mask=0,
                                                                   match=rule.get_match())
            self.datapath.send_msg(req)
            self.round_status[rule] = None
