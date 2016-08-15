from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_5

from SDM.apps.PullingController import PullingController
from SDM.rules.FlagsSrcRule import FlagsSrcRule
from SDM.rules.SynSrcRule import SynSrcRule
from SDM.rules.TCPIPSrcRule import TCPIPSrcRule


class SrcSynPullingController(PullingController):
    OFP_VERSIONS = [ofproto_v1_5.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SrcSynPullingController, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        with self.res_lock:
            msg = ev.msg
            body = msg.body
            main_datapath = self.datapaths[msg.datapath]
            syn_rule = None
            syn_packets = 0
            tcp_rule = None
            tcp_packets = 0
            current_rate = 0
            self.info('datapath         '
                      'rule                                                     '
                      'packets ')

            self.info('---------------- '
                      '-------------------------------------------------------- '
                      '--------')
            for stat in sorted([flow for flow in body],
                               key=lambda f: (f.match['ipv4_src'])):
                ipv4_src = stat.match['ipv4_src']
                if len(ipv4_src) > 2:  # no mask returned, only IPv4 so len is len of string and not tuple.
                    assert len(ipv4_src.split(".")) == 4
                    ipv4_string = ipv4_src
                    subnet_string = "255.255.255.255"
                else:
                    ipv4_string = ipv4_src[0]
                    subnet_string = ipv4_src[1]

                try:
                    tcp_flags = stat.match['tcp_flags']
                    rule = FlagsSrcRule(msg.datapath, ipv4_string, subnet_string, stat.table_id, stat.priority,
                                         tcp_flags, None)
                    syn_rule = rule
                    syn_packets = stat.packet_count
                except KeyError:
                    rule = TCPIPSrcRule(msg.datapath, ipv4_string, subnet_string, stat.table_id, stat.priority, None)
                    tcp_rule = rule
                    tcp_packets = stat.packet_count

            rule = SynSrcRule.from_sub_rules(tcp_rule, syn_rule, None)
            prev_tcp_count = main_datapath.frontier_values[rule]['tcp_packets']
            prev_syn_count = main_datapath.frontier_values[rule]['syn_packets']
            main_datapath.frontier_values[rule] = {'tcp_packets': tcp_packets, 'syn_packets': syn_packets}

            try:
                current_rate = ((1.0 * syn_packets - prev_syn_count) / (
                    (tcp_packets - prev_tcp_count) + (syn_packets - prev_syn_count))) * 100
            except ZeroDivisionError:
                pass

            self.info('%016x %56s %08d',
                      msg.datapath.id,
                      syn_rule,
                      syn_packets - prev_syn_count)
            self.info('%016x %56s %08d',
                      msg.datapath.id,
                      tcp_rule,
                      tcp_packets - prev_tcp_count)
            self.info('Syn rate for the rule %s is: %f %%', rule, current_rate)
            self.handle_rule_stat(rule, current_rate, main_datapath)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def get_rule_threshold(self, rule):
        return 2
