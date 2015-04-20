from operator import attrgetter

from src.SDM.apps import simple_switch_stp_13
from src.SDM.util import get_dirs, get_params
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub


class PullingMonitor(simple_switch_stp_13.STP13):

    def __init__(self, *args, **kwargs):
        super(PullingMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.dirs = get_dirs()
        self.params = get_params(self.dirs)

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            hub.sleep(self.params['RunParameters']['timeStep'])
            for dp in self.datapaths.values():
                self._request_stats(dp)

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

#        req = parser.OFPPortStatsRequest(datapath, 0, 1)
#        datapath.send_msg(req)

#        req = parser.OFPMeterStatsRequest(datapath, 0, ofproto.OFPM_ALL)
#        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPMeterStatsReply, MAIN_DISPATCHER)
    def _meter_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         '
                         'bytes            '
                         'duration         '
                         'KBPS                     ')
        self.logger.info('---------------- '
                         '---------------- '
                         '---------------- '
                         '------------------------ ')
        for stat in body:
            self.logger.info('%016x %16x %16x %24f',
                             ev.msg.datapath.id,
                             stat.byte_in_count, (1000*stat.duration_sec+stat.duration_nsec)/1000,
                             stat.byte_in_count / (1000*stat.duration_sec+stat.duration_nsec)/1000)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         '
                         'in-port  eth-dst           '
                         'packets  bytes')
        self.logger.info('---------------- '
                         '-------- ----------------- '
                         '-------- --------')
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda f: (f.match['in_port'],
                                             f.match['eth_dst'])):

            self.logger.info('%016x %8x %17s %8d %8d',
                             ev.msg.datapath.id,
                             stat.match['in_port'], stat.match['eth_dst'],
                             stat.packet_count, stat.byte_count)

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d', 
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)
