import socket
import logging
import select
from threading import Thread
from time import sleep

from ryu.ofproto import ofproto_common
from ryu.ofproto import ofproto_parser
from ryu.ofproto import ofproto_protocol
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto import ofproto_v1_2
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_4
from ryu.ofproto import ofproto_v1_5
from ryu import exception

from src.SDM.util import bytes_to_ipv4


class ProxyThread(Thread, ofproto_protocol.ProtocolDesc):
    def __init__(self, controllerIP, controllerPort, protocol):
        Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Created ProxyThread, %s:%s", controllerIP, controllerPort)
        self.protocol = protocol
        self.OFP_VERSIONS = []
        if not self.protocol:
            self.logger.info("Default protocol: OF13")
            ofproto_protocol.ProtocolDesc.__init__(self, 0x04)
        else:
            self.logger.info("Non default protocol: %s", protocol)
            for p in protocol[0].split(","):
                v = int(p[-1:])
                if v == 0:
                    ofproto_protocol.ProtocolDesc.__init__(ofproto_v1_0.OFP_VERSION)
                if v == 2:
                    ofproto_protocol.ProtocolDesc.__init__(ofproto_v1_2.OFP_VERSION)
                if v == 3:
                    ofproto_protocol.ProtocolDesc.__init__(ofproto_v1_3.OFP_VERSION)
                if v == 4:
                    ofproto_protocol.ProtocolDesc.__init__(ofproto_v1_4.OFP_VERSION)
                if v == 5:
                    ofproto_protocol.ProtocolDesc.__init__(ofproto_v1_5.OFP_VERSION)
        self.controllerIP = controllerIP
        self.controllerPort = controllerPort
        self.myIP = "127.0.0.1"
        self.myPort = controllerPort + 1
        self.switchPort = None
        self.switchIP = None
        self.toControllerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fromSwitchSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = True
        self.channel = {}

    def run(self):
        sleep(1)
        self.fromSwitchSock.bind((self.myIP, self.myPort))
        self.logger.debug("Binding to: %s:%s", self.myIP, self.myPort)
        self.fromSwitchSock.settimeout(None)
        self.fromSwitchSock.listen(socket.SOMAXCONN)
        self.logger.debug("listen to: %s:%s", self.myIP, self.myPort)
        self.logger.debug("accepting: %s:%s", self.myIP, self.myPort)
        client, address = self.fromSwitchSock.accept()
        self.logger.debug("accepted: %s:%s", client, address)
        self.toControllerSock.connect((self.controllerIP, self.controllerPort))
        self.logger.debug("Connected to: %s:%s", self.controllerIP, self.controllerPort)
        self.channel[client] = self.toControllerSock
        self.channel[self.toControllerSock] = client
        while self.connected:
            client.settimeout(None)
            inputready, outputready, exceptready = select.select([client, self.toControllerSock], [], [])
            for s in inputready:
                self.recv_msg(s)
                #msg, buf = self.recv_msg(s)
                #self.logger.info("msg from %s: %s", s.getpeername(), buf)
                #self.handle_raw_msg(s, buf)
        client.close()
        self.toControllerSock.close()
        self.fromSwitchSock.close()

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

                self.handle_raw_msg(from_sock,buf[:required_len])

                buf = buf[required_len:]
                required_len = ofproto_common.OFP_HEADER_SIZE

                if len(buf) == 0:
                    return

                count += 1
                if count > 2048:
                    return

    def handle_msg(self, from_sock, msg, buf):
        self.logger.debug("msg ser, to %s: %s", self.channel[from_sock].getpeername(), msg)
        self.channel[from_sock].sendall(buf)

    def handle_raw_msg(self, from_sock, data):
        hex_data = ':'.join('{:02x}'.format(x) for x in data)
        if len(data) != 0:
            self.logger.info("received data from %s: %s", from_sock, hex_data)
            if hex_data.split(":")[1] == "0e" and hex_data.split(":")[24] == "01":
                    ip_addr = bytes_to_ipv4(str(data[62:66]))
                    mask = bytes_to_ipv4(str(data[66:70]))
                    self.logger.debug("ip_bytes %s | mask_bytes %s", ':'.join('{:02x}'.format(x) for x in data[62:66]), ':'.join('{:02x}'.format(x) for x in data[66:70]))
                    self.logger.info("Monitoring %s:%s", ip_addr, mask)
                    self.monitor()
            self.channel[from_sock].sendall(data)
            self.logger.debug("sent data to %s: %s", self.channel[from_sock], hex_data)

    def monitor(self):
        pass

    def stop(self):
        self.connected = False


class MiddleWare():
    def __init__(self, controllerIP="127.0.0.1", switchIP=None, controllerPort=6633, switchPort=None, protocols=None):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Created MiddleWare")
        self.controllerIP = controllerIP
        self.switchIP = switchIP
        self.controllerPort = controllerPort
        self.switchPort = switchPort
        self.fromSwitchProxy = ProxyThread(controllerIP, controllerPort, protocols)

    def start(self):
        self.fromSwitchProxy.daemon = True
        self.fromSwitchProxy.start()

    def stop(self):
        self.fromSwitchProxy.stop()

