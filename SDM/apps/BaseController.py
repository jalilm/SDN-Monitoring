import mmap
from multiprocessing import Lock
from time import time

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import ethernet
from ryu.lib.packet import packet
from ryu.ofproto import ofproto_v1_3

from SDM.rules.Rule import Rule
from SDM.util import *


class BaseController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(BaseController, self).__init__(*args, **kwargs)
        self.dirs = get_dirs()
        self.parameters = get_params(self.dirs)
        self.datapaths = {}
        self.res_lock = Lock()

    def debug(self, msg, *args, **kwargs):
        self.logger.debug('{0:.5f}'.format(time()) + " " + msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info('{0:.5f}'.format(time()) + " " + msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        self.logger.warn('{0:.5f}'.format(time()) + " " + msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error('{0:.5f}'.format(time()) + " " + msg, *args, **kwargs)

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
        if len(datapath.ports) == 3:
            datapath_class = get_class(self.parameters['RunParameters']['Datapath'])
            self.datapaths[datapath] = datapath_class(datapath)
            self.datapaths[datapath].set_route_tables()
            self.datapaths[datapath].set_main_monitor_table()
        else:
            assert False
        self.after_datapaths_construction()

    def after_datapaths_construction(self):
        pass

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        assert False

    def handle_rule_stat(self, rule, current_stat, main_datapath):
        # noinspection PyTypeChecker
        if current_stat > self.get_rule_threshold(rule):
            if not main_datapath.increase_monitoring_level(rule):
                self.info('Alert! traffic of flow %s is above threshold', rule)
                self.issue_alert()
            else:
                self.info('Finer monitoring rules for %s were added', rule)
        elif current_stat <= (self.get_rule_threshold(rule) / 2):
            res = main_datapath.reduce_monitoring_level(rule)
            if not res[0]:
                self.info('Not reducing monitoring level for %s: %s', rule, res[1])
            else:
                self.info('Removed finer monitoring rules for %s and %s', res[1], res[2])
        else:
            self.info('Keeping the rule %s for monitoring', rule)
            main_datapath.keep_monitoring_level(rule)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def get_rule_threshold(self, rule):
        assert False

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        dpid = ev.msg.datapath.id
        in_port = ev.msg.match['in_port']
        pkt = packet.Packet(ev.msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        dst = eth.dst
        src = eth.src
        self.warn("Packet in event %016x %s %s %s", dpid, src, dst, in_port)

    def issue_alert(self):
        with open(self.parameters['General']['sharedMemFilePath'], "r+b") as _file:
            mem_map = mmap.mmap(_file.fileno(), 0)
            mem_map[:6] = self.parameters['General']['alertToken']
            mem_map.close()
