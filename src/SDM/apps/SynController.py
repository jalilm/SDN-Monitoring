from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_5
from src.SDM.apps.TracePullingController import TracePullingController
from src.SDM.nodes.SynDatapath import SynDatapath
from src.SDM.rules.FlagsDestRule import FlagsDestRule
from src.SDM.rules.TCPIPDestRule import TCPIPDestRule
from src.SDM.rules.SynDestRule import SynDestRule

class SynController(TracePullingController):
    OFP_VERSIONS = [ofproto_v1_5.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SynController, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, CONFIG_DISPATCHER)
    def multipart_reply_handler(self, ev):
        datapath = ev.msg.datapath
        # if len(datapath.ports) == 2:
        # For OVS there is a down local port.
        if len(datapath.ports) == 3:
            self.datapaths[datapath] = SynDatapath(datapath)
            self.datapaths[datapath].set_route_tables()
            self.datapaths[datapath].set_main_monitor_table()
        else:
            assert False

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        with self.res_lock:
            msg = ev.msg
            body = msg.body
            main_datapath = self.datapaths[msg.datapath]
            syn_rule = None
            syn_packets = 0
            tcp_rule = None
            tcp_packets = 0
            self.info('datapath         '
                      'rule                                                     '
                      'packets ')

            self.info('---------------- '
                      '-------------------------------------------------------- '
                      '--------')
            for stat in sorted([flow for flow in body],
                               key=lambda f: (f.match['ipv4_dst'])):
                ipv4_dst = stat.match['ipv4_dst']
                if len(ipv4_dst) > 2:  # no mask returned, only IPv4 so len is len of string and not tuple.
                    assert len(ipv4_dst.split(".")) == 4
                    ipv4_string = ipv4_dst
                    subnet_string = "255.255.255.255"
                else:
                    ipv4_string = ipv4_dst[0]
                    subnet_string = ipv4_dst[1]

                try:
                    tcp_flags = stat.match['tcp_flags']
                    rule = FlagsDestRule(msg.datapath, ipv4_string, subnet_string, stat.table_id, stat.priority, tcp_flags, None)
                    syn_rule = rule
                    syn_packets = stat.packet_count
                except KeyError:
                    rule = TCPIPDestRule(msg.datapath, ipv4_string, subnet_string, stat.table_id, stat.priority, None)
                    tcp_rule = rule
                    tcp_packets = stat.packet_count

                self.info('%016x %56s %08d',
                          msg.datapath.id,
                          rule,
                          stat.packet_count)

            rule = SynDestRule.from_sub_rules(tcp_rule, syn_rule, None)

            try:
                main_datapath.frontier_values[rule] = ((1.0 * syn_packets) / (syn_packets+tcp_packets)) * 100
            except ZeroDivisionError:
                pass
            self.info('Syn rate for the rule %s is: %f %%', rule, main_datapath.frontier_values[rule])

            if main_datapath.frontier_values[rule] > self.get_rule_threshold(rule):
                if not main_datapath.increase_monitoring_level(rule):
                    self.info('Alert! traffic of flow %s is above threshold', rule)
                    self.alert()
                else:
                    self.info('Finer monitoring rules for %s were added', rule)
            elif main_datapath.frontier_values[rule] <= (self.get_rule_threshold(rule) / 2):
                res = main_datapath.reduce_monitoring_level(rule)
                if not res[0]:
                    self.info('Not reducing monitoring level for %s: %s', rule, res[1])
                else:
                    self.info('Removed finer monitoring rules for %s and %s', res[1], res[2])
            else:
                self.info('Keeping the rule %s for monitoring', rule)
                main_datapath.keep_monitoring_level(rule)

    def get_rule_threshold(self, rule):
        return 2

    # @set_ev_cls(ofp_event.EventOFPFlowDescReply, MAIN_DISPATCHER)
    # def _flow_desc_reply_handler(self, ev):
    #     with self.res_lock:
    #         body = ev.msg.body
    #         print body
    #         main_datapath = self.datapaths[ev.msg.datapath]
    #
    #         for stat in sorted([flow for flow in body],
    #                            key=lambda f: (f.match['ipv4_dst'])):
    #             self.info(stat)
