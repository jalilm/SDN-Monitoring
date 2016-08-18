from SDM.nodes.MiddleWare import MiddleWare
from SDM.rules.SynDestPushingRule import SynDestPushingRule
from SDM.util import bytes_to_ipv4


# noinspection PyAbstractClass
class SynMiddleWare(MiddleWare):
    def __init__(self, ovs_switch, controller_ip="127.0.0.1", switch_ip=None, controller_port=6633, switch_port=None,
                 protocols=None):
        super(SynMiddleWare, self).__init__(ovs_switch, controller_ip, switch_ip, controller_port, switch_port,
                                            protocols)
        self.frontier_default_value = {'tcp_packets': 0, 'syn_packets': 0}
        self.logger.info("Created SynMiddleWare")

    def handle_results(self, res, rule):
        if not res:
            return
        lines = res.split('\r')
        syn_packets = 0
        tcp_packets = 0
        current_rate = 0
        for line in lines[1:3]:
            stat = {}
            res = line.replace('\r', ' ').replace('\n', ' ').replace(',', ' ').split(' ')
            res = [x for x in res if "=" in x]
            for r in res:
                stat[r.split('=')[0]] = r.split('=')[1]
            try:
                # noinspection PyUnusedLocal
                f = stat['tcp_flags']
                syn_packets = int(stat['n_packets'])
            except KeyError:
                try:
                    tcp_packets = int(stat['n_packets'])
                except KeyError:
                    self.logger.info('Request sent faster than switch ramp up')

        prev_tcp_count = self.frontier_values[rule]['tcp_packets']
        prev_syn_count = self.frontier_values[rule]['syn_packets']
        self.frontier_values[rule] = {'tcp_packets': tcp_packets, 'syn_packets': syn_packets}
        try:
            current_rate = ((1.0 * syn_packets - prev_syn_count) / (
                (tcp_packets - prev_tcp_count) + (syn_packets - prev_syn_count))) * 100
        except ZeroDivisionError:
            pass

        self.logger.info('rule                                                     '
                         'syn-packets tcp-packets syn-rate ')

        self.logger.info('-------------------------------------------------------- '
                         '----------- ----------- ---------')

        self.logger.info('%56s %011d %011d %03.6f', rule, syn_packets - prev_syn_count, tcp_packets - prev_tcp_count,
                         current_rate)
        self.handle_rule_stat(rule, current_rate)

    def create_rule(self, ip_addr, mask):
        return SynDestPushingRule(self.ovs_switch, self.datapath, ip_addr, mask, 1, 2, None, self.protocol_str)

    def handle_raw_msg(self, data):
        hex_data = ':'.join('{:02x}'.format(x) for x in data)
        if len(data) != 0:
            if hex_data.split(":")[1] == "0e" and hex_data.split(":")[24] == "01" and len(data) == 104:
                ip_addr = bytes_to_ipv4(str(data[67:71]))
                mask = bytes_to_ipv4(str(data[71:75]))
                self.logger.debug("ip_bytes %s | mask_bytes %s", ':'.join('{:02x}'.format(x) for x in data[67:71]),
                                  ':'.join('{:02x}'.format(x) for x in data[71:75]))
                self.logger.debug("Monitoring %s:%s", ip_addr, mask)
                self.monitor(ip_addr, mask)
            return data
        else:
            return None

    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def get_rule_threshold(self, rule):
        return 2
