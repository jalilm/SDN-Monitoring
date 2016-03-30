from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from src.SDM.rules.IPDestRule import IPDestRule
from src.SDM.apps.PullingController import PullingController


class BWPullingController(PullingController):
    def __init__(self, *args, **kwargs):
        super(BWPullingController, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        with self.res_lock:
            body = ev.msg.body
            main_datapath = self.datapaths[ev.msg.datapath]

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

                rule = IPDestRule(ev.msg.datapath, ipv4_string, subnet_string, stat.table_id, 0, None)

                self.info('datapath         '
                          'ipv4-dst                           '
                          'current bandwidth  duration           bytes')
                self.info('---------------- '
                          '---------------------------------- '
                          '------------------ ------------------ --------')

                try:
                    new_byte_count = stat.byte_count - main_datapath.frontier_values[rule]['byte_count']
                    new_duration = stat.duration_sec + (stat.duration_nsec / 1000000000.0) - \
                                   main_datapath.frontier_values[rule]['duration']
                    current_rate = new_byte_count / new_duration
                    main_datapath.frontier_values[rule] = {
                    'duration': stat.duration_sec + (stat.duration_nsec / 1000000000.0), 'byte_count': stat.byte_count}
                except ZeroDivisionError:
                    if stat.byte_count == 0:
                        self.info('%016x %34s %018.9f %018.9f %08d',
                                  ev.msg.datapath.id,
                                  rule,
                                  float("nan"),
                                  0,
                                  0)
                        self.info('Keeping the rule %s for monitoring, not enough data received', rule)
                        main_datapath.keep_monitoring_level(rule)
                        continue
                    else:
                        current_rate = float("inf")

                self.info('%016x %34s %018.9f %018.09f %08d',
                          ev.msg.datapath.id,
                          rule,
                          current_rate,
                          new_duration,
                          new_byte_count)
                self.handle_rule_stat(rule, current_rate, main_datapath)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def get_rule_threshold(self, rule):
        return 1500000/(self.parameters['RunParameters']['numHH']/1.0)
