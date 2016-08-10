import logging
import mmap
import select
import socket
from datetime import datetime
from threading import *
from threading import Thread
from time import sleep

from ryu.lib import hub
from ryu.ofproto import ofproto_common
from ryu.ofproto import ofproto_parser
from ryu.ofproto import ofproto_protocol
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto import ofproto_v1_2
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_4
from ryu.ofproto import ofproto_v1_5

from SDM import Strategy


class ProxyThread(Thread):
    def __init__(self, middleware, controller_ip, controller_port):
        super(ProxyThread, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Created ProxyThread, %s:%s", controller_ip, controller_port)
        self.middleware = middleware
        self.controllerIP = controller_ip
        self.controllerPort = controller_port
        self.myIP = "127.0.0.1"
        self.myPort = controller_port + 1
        self.switchPort = None
        self.switchIP = None
        self.toControllerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fromSwitchSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fromMiddlewareSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = True
        self.channel = {}

    def run(self):
        self.fromMiddlewareSock.bind((self.myIP, self.myPort + 1))
        self.logger.debug("Binding to: %s:%s", self.myIP, self.myPort + 1)
        self.fromMiddlewareSock.settimeout(None)
        self.fromMiddlewareSock.listen(socket.SOMAXCONN)
        mw_client, mw_addr = self.fromMiddlewareSock.accept()
        self.channel[mw_client] = self.toControllerSock

        sleep(1)

        self.fromSwitchSock.bind((self.myIP, self.myPort))
        self.logger.debug("Binding to: %s:%s", self.myIP, self.myPort)
        self.fromSwitchSock.settimeout(None)
        self.fromSwitchSock.listen(socket.SOMAXCONN)
        self.logger.debug("listen to: %s:%s", self.myIP, self.myPort)
        self.logger.debug("accepting: %s:%s", self.myIP, self.myPort)
        client, address = self.fromSwitchSock.accept()
        self.logger.debug("accepted: %s:%s", client, address)
        self.channel[client] = self.toControllerSock

        self.toControllerSock.connect((self.controllerIP, self.controllerPort))
        self.logger.debug("Connected to: %s:%s", self.controllerIP, self.controllerPort)
        self.channel[self.toControllerSock] = client

        while self.connected:
            mw_client.settimeout(None)
            client.settimeout(None)
            inputready, outputready, exceptready = select.select([mw_client, client, self.toControllerSock], [], [])
            for s in inputready:
                self.recv_msg(s)

        mw_client.close()
        client.close()
        self.toControllerSock.close()
        self.fromSwitchSock.close()
        self.fromMiddlewareSock.close()

    def recv_msg(self, from_sock):
        buf = bytearray()
        required_len = ofproto_common.OFP_HEADER_SIZE
        count = 0
        while self.connected:
            ret = from_sock.recv(required_len)
            if len(ret) == 0:
                self.connected = False
                break
            buf += ret
            while len(buf) >= required_len:
                (version, msg_type, msg_len, xid) = ofproto_parser.header(buf)
                required_len = msg_len
                if len(buf) < required_len:
                    break

                hex_data = ':'.join('{:02x}'.format(x) for x in buf[:required_len])
                self.logger.debug("received data from %s: %s", from_sock, hex_data)
                data = self.middleware.handle_raw_msg(buf[:required_len])
                if data:
                    hex_data = ':'.join('{:02x}'.format(x) for x in data)
                    self.channel[from_sock].sendall(data)
                    self.logger.debug("sent data to %s: %s", self.channel[from_sock], hex_data)

                buf = buf[required_len:]
                required_len = ofproto_common.OFP_HEADER_SIZE

                if len(buf) == 0:
                    return

                count += 1
                if count > 2048:
                    return

    def stop(self):
        self.connected = False


class MonitorThread(Thread):
    def __init__(self, middleware, time_step, condition):
        super(MonitorThread, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Created Monitoring Thread")
        self.middleware = middleware
        self.time_step = time_step
        self.condition = condition
        self.connected = True

    def run(self):
        time_step_number = 0
        self.logger.info('Waiting to get notified')
        with self.condition:
            self.condition.wait()
        self.logger.info('Got instruction to start monitoring')
        while self.connected:
            hub.sleep(self.time_step)
            time_step_number += 1
            self.logger.info('')
            self.logger.info('Time step #%d - ' + datetime.now().strftime('%H:%M:%S.%f'), time_step_number)
            self.logger.debug('Getting stats request')
            self.middleware.request_stats()

    def stop(self):
        self.connected = False


class MiddleWare(Strategy):
    def __init__(self, ovs_switch, controller_ip="127.0.0.1", switch_ip=None, controller_port=6633, switch_port=None,
                 protocols=None, first_monitoring_table=1):
        super(MiddleWare, self).__init__(first_monitoring_table)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Created MiddleWare")
        self.ovs_switch = ovs_switch
        self.controllerIP = controller_ip
        self.switchIP = switch_ip
        self.controllerPort = controller_port
        self.switchPort = switch_port
        self.protocols = protocols
        self.dirs = get_dirs()
        self.params = get_params(self.dirs)
        self.condition = Condition()
        self.toProxySock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fromSwitchProxy = ProxyThread(self, controller_ip, controller_port)
        self.monitor_thread = MonitorThread(self, self.params['RunParameters']['timeStep'], self.condition)
        self.connected = False
        self.counters = 0
        self.alerts = []
        if not self.protocols:
            self.logger.debug("Default protocol: OF13")
            self.datapath = ofproto_protocol.ProtocolDesc(0x04)
            self.protocol_str = "OpenFlow13"
        else:
            self.logger.debug("Non default protocol: %s", protocols)
            for p in protocols[0].split(","):
                v = int(p[-1:])
                if v == 0:
                    self.datapath = ofproto_protocol.ProtocolDesc(ofproto_v1_0.OFP_VERSION)
                    self.protocol_str = "OpenFlow10"
                if v == 2:
                    self.datapath = ofproto_protocol.ProtocolDesc(ofproto_v1_2.OFP_VERSION)
                    self.protocol_str = "OpenFlow12"
                if v == 3:
                    self.datapath = ofproto_protocol.ProtocolDesc(ofproto_v1_3.OFP_VERSION)
                    self.protocol_str = "OpenFlow13"
                if v == 4:
                    self.datapath = ofproto_protocol.ProtocolDesc(ofproto_v1_4.OFP_VERSION)
                    self.protocol_str = "OpenFlow14"
                if v == 5:
                    self.datapath = ofproto_protocol.ProtocolDesc(ofproto_v1_5.OFP_VERSION)
                    self.protocol_str = "OpenFlow15"

    def monitor(self, ip_addr, mask):
        rule = self.create_rule(ip_addr, mask)
        self.add_monitoring_rule(rule)
        with self.condition:
            self.condition.notify_all()

    def start(self):
        sleep(5)
        self.monitor_thread.daemon = True
        self.fromSwitchProxy.daemon = True
        self.connected = True
        self.monitor_thread.start()
        self.fromSwitchProxy.start()
        sleep(1)
        self.toProxySock.connect(("127.0.0.1", self.controllerPort + 2))
        self.logger.debug("Connected to Proxy: %s", self.controllerPort + 2)

    def stop(self):
        self.connected = False
        self.fromSwitchProxy.stop()
        self.monitor_thread.stop()
        with open(self.params['General']['sharedMemFilePath'], "r+b") as _file:
                mem_map = mmap.mmap(_file.fileno(), 0)
                mem_map[:6] = self.params['General']['alertToken']
                mem_map.close()

    def add_monitoring_rule(self, rule):
        super(MiddleWare, self).add_monitoring_rule(rule)
        self.round_status[rule] = None
        self.counters += 1

    def request_stats(self):
        finished_last_round = self.received_all_replys()
        while not finished_last_round:
            finished_last_round = self.received_all_replys()

        self.round_status = {}
        self.frontier = self.next_frontier
        if len(self.next_frontier) > self.counters:
            self.counters = len(self.next_frontier)
        self.logger.info('current number of counters is: %d', len(self.next_frontier))
        self.next_frontier = []
        for rule in self.frontier:
            self.round_status[rule] = None

        for rule in self.frontier:
            res = self.get_rule_stats(rule)
            self.handle_results(res, rule)

    def set_main_monitor_table(self):
        raise NotImplementedError

    def handle_results(self, res, rule):
        raise NotImplementedError

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def get_rule_threshold(self, rule):
        raise NotImplementedError

    def handle_rule_stat(self, rule, current_stat):
        if current_stat > self.get_rule_threshold(rule):
            if not self.increase_monitoring_level(rule):
                self.issue_alert(rule)
            else:
                self.logger.info('Finer monitoring rules for %s were added', rule)
        elif current_stat <= (self.get_rule_threshold(rule) / 2):
            r = self.reduce_monitoring_level(rule)
            if not r[0]:
                self.logger.info('Not reducing monitoring level for %s: %s', rule, r[1])
            else:
                self.logger.info('Removed finer monitoring rules for %s and %s', r[1], r[2])
        else:
            self.logger.info('Keeping the rule %s for monitoring', rule)
            self.keep_monitoring_level(rule)

    # noinspection PyMethodMayBeStatic
    def get_rule_stats(self, rule):
        return rule.get_stats()

    def issue_alert(self, rule):
        if rule in self.alerts:
            return
        self.alerts.append(rule)
        self.logger.debug('Alert traffic of flow %s is above threshold', rule)
        self.logger.info("Alert! at MiddleWare for Rule: %s", rule)
        data = bytearray(rule.__str__())
        msg = self.datapath.ofproto_parser.OFPExperimenter(self.datapath, 0xabcdefab, 0x00000000, data)
        msg.serialize()
        self.toProxySock.sendall(msg.buf)
        if len(self.alerts) == self.params['RunParameters']['numHH']:
            self.logger.info('Maximal number of counters is: %d', self.counters)
            self.stop()

    def create_rule(self, ip_addr, mask):
        raise NotImplementedError

    def handle_raw_msg(self, data):
        raise NotImplementedError
