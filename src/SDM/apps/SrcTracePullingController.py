from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from src.SDM.rules.IPSrcRule import IPSrcRule
from src.SDM.nodes.SrcTraceDatapath import SrcTraceDatapath
from src.SDM.apps.TracePullingController import TracePullingController

class SrcTracePullingController(TracePullingController):

    def __init__(self, *args, **kwargs):
        super(SrcTracePullingController, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, CONFIG_DISPATCHER)
    def multipart_reply_handler(self, ev):
        datapath = ev.msg.datapath
        # if len(datapath.ports) == 2:
        # For OVS there is a down local port.
        if len(datapath.ports) == 3:
            self.datapaths[datapath] = SrcTraceDatapath(datapath)
            self.datapaths[datapath].set_route_tables()
            self.datapaths[datapath].set_main_monitor_table()
        else:
            assert False

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        with self.res_lock:
            body = ev.msg.body
            main_datapath = self.datapaths[ev.msg.datapath]

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

                rule = IPSrcRule(ev.msg.datapath, ipv4_string, subnet_string, stat.table_id, 0, None)

                main_datapath.frontier_bw[rule] = stat.byte_count / (
                    stat.duration_sec + (stat.duration_nsec / 1000000000.0))

                if main_datapath.frontier_bw[rule] > self.get_rule_limit(rule):
                    self.info('datapath         '
                                     'ipv4-src                           '
                                     'bandwidth          duration bytes')
                    self.info('---------------- '
                                     '---------------------------------- '
                                     '------------------ -------- --------')

                    self.info('%016x %34s %018.9f %08d %08d',
                                     ev.msg.datapath.id,
                                     rule,
                                     main_datapath.frontier_bw[rule],
                                     stat.duration_sec,
                                     stat.byte_count)
                    if not main_datapath.increase_monitoring_level(rule):
                        self.info('Alert! traffic of flow %s is above threshold', rule)
                    else:
                        self.info('Finer monitoring rules for %s were added', rule)
                elif main_datapath.frontier_bw[rule] <= (self.get_rule_limit(rule) / 2):
                    self.info('datapath         '
                                     'ipv4-src                           '
                                     'bandwidth          duration bytes')
                    self.info('---------------- '
                                     '---------------------------------- '
                                     '------------------ -------- --------')

                    self.info('%016x %34s %018.9f %08d %08d',
                                     ev.msg.datapath.id,
                                     rule,
                                     main_datapath.frontier_bw[rule],
                                     stat.duration_sec,
                                     stat.byte_count)
                    res = main_datapath.reduce_monitoring_level(rule)
                    if not res[0]:
                        self.info('Not reducing monitoring level for %s: %s', rule, res[1])
                    else:
                        self.info('Removed finer monitoring rules for %s and %s', res[1], res[2])
                else:
                    self.info('datapath         '
                                     'ipv4-src                           '
                                     'bandwidth          duration bytes')
                    self.info('---------------- '
                                     '---------------------------------- '
                                     '------------------ -------- --------')

                    self.info('%016x %34s %018.9f %08d %08d',
                                     ev.msg.datapath.id,
                                     rule,
                                     main_datapath.frontier_bw[rule],
                                     stat.duration_sec,
                                     stat.byte_count)
                    self.info('Keeping the rule %s for monitoring', rule)
                    main_datapath.keep_monitoring_level(rule)
