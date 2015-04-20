from multiprocessing import Lock

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib import hub
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from src.SDM.nodes import TraceDatapath
from src.SDM.util import *
from src.SDM.rules.IPDestRule import IPDestRule
from src.SDM.rules.Rule import Rule
from src.SDM.rules.InPortRule import InPortRule


class TracePullingController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TracePullingController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.dirs = get_dirs()
        self.params = get_params(self.dirs)
        self.datapaths = {}
        self.limits = {}
        self.res_lock = Lock()

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        rule = Rule(datapath, 0, 0)
        rule.add_flow_and_apply_actions(actions)

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, CONFIG_DISPATCHER)
    def multipart_reply_handler(self, ev):
        datapath = ev.msg.datapath
        # if len(datapath.ports) == 2:
        # For OVS there is a down local port.
        if len(datapath.ports) == 3:
            self.datapaths[datapath] = TraceDatapath(datapath)
            self.datapaths[datapath].set_route_tables()
            self.datapaths[datapath].set_main_monitor_table()
        else:
            assert False

    def _monitor(self):
        time_step_number = 0
        while True:
            hub.sleep(self.params['RunParameters']['timeStep'])
            time_step_number += 1
            self.logger.info('')
            self.logger.info('Time step #%d', time_step_number)
            for dp in self.datapaths:
                dpp = self.datapaths[dp]
                self.logger.info('Sending stats request: %016x', dpp.id)
                dpp.request_stats()

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
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

                main_datapath.frontier_bw[rule] = stat.byte_count / (
                    stat.duration_sec + (stat.duration_nsec / 1000000000.0))

                if main_datapath.frontier_bw[rule] > self.get_rule_limit(rule):
                    self.logger.info('datapath         '
                                     'ipv4-dst                           '
                                     'bandwidth          duration bytes')
                    self.logger.info('---------------- '
                                     '---------------------------------- '
                                     '------------------ -------- --------')

                    self.logger.info('%016x %34s %018.9f %08d %08d',
                                     ev.msg.datapath.id,
                                     rule,
                                     main_datapath.frontier_bw[rule],
                                     stat.duration_sec,
                                     stat.byte_count)
                    if not main_datapath.increase_monitoring_level(rule):
                        self.logger.info('Alert! traffic of flow %s is above threshold', rule)
                    else:
                        self.logger.info('Finer monitoring rules for %s were added', rule)
                elif main_datapath.frontier_bw[rule] <= (self.get_rule_limit(rule) / 2):
                    self.logger.info('datapath         '
                                     'ipv4-dst                           '
                                     'bandwidth          duration bytes')
                    self.logger.info('---------------- '
                                     '---------------------------------- '
                                     '------------------ -------- --------')

                    self.logger.info('%016x %34s %018.9f %08d %08d',
                                     ev.msg.datapath.id,
                                     rule,
                                     main_datapath.frontier_bw[rule],
                                     stat.duration_sec,
                                     stat.byte_count)
                    res = main_datapath.reduce_monitoring_level(rule)
                    if not res[0]:
                        self.logger.info('Not reducing monitoring level for %s: %s', rule, res[1])
                    else:
                        self.logger.info('Removed finer monitoring rules for %s and %s', res[1], res[2])
                else:
                    self.logger.info('datapath         '
                                     'ipv4-dst                           '
                                     'bandwidth          duration bytes')
                    self.logger.info('---------------- '
                                     '---------------------------------- '
                                     '------------------ -------- --------')

                    self.logger.info('%016x %34s %018.9f %08d %08d',
                                     ev.msg.datapath.id,
                                     rule,
                                     main_datapath.frontier_bw[rule],
                                     stat.duration_sec,
                                     stat.byte_count)
                    self.logger.info('Keeping the rule %s for monitoring', rule)
                    main_datapath.keep_monitoring_level(rule)

    def get_rule_limit(self, rule):
        return 3000000

    # def get_rule_limit(self, rule):
    # self.logger.info('get rule limit for %s', rule)
    # if self.limits.get((rule.ipv4_string, rule.subnet_string)) != None:
    #         return self.limits[(rule.ipv4_string, rule.subnet_string)]
    #     if rule.subnet_string == "255.255.255.255":
    #         self.limits[(rule.ipv4_string, rule.subnet_string)] = self.params['FlowLimits'].get(rule.ipv4_string, 0)
    #         return self.limits[(rule.ipv4_string, rule.subnet_string)]
    #     for r in rule.get_finer_rules():
    #         self.limits[(rule.ipv4_string, rule.subnet_string)] = self.limits.get(
    #             (rule.ipv4_string, rule.subnet_string), 0) + self.get_rule_limit(r)
    #     return self.limits[(rule.ipv4_string, rule.subnet_string)]

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %016x %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            rule = InPortRule(datapath, 0, in_port, 0, dst)
            rule.add_flow_and_apply_actions(actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
