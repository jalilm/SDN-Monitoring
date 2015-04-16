from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_5
from src.pulling.SynDatapath import SynDatapath
from src.pulling.TracePullingController import TracePullingController

#import sys
#sys.path.append('/home/sdm/.pycharm_helpers/pycharm-debug.egg')
#import pydevd
#pydevd.settrace('132.68.42.133', port=58397, stdoutToServer=True, stderrToServer=True, suspend=False ,trace_only_current_thread=False)

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
            body = ev.msg.body
            print body
            main_datapath = self.datapaths[ev.msg.datapath]

            for stat in sorted([flow for flow in body],
                               key=lambda f: (f.match['ipv4_dst'])):
                print stat
