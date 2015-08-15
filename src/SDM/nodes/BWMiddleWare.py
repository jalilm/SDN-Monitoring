import logging

from src.SDM.nodes.MiddleWare import MiddleWare
from src.SDM.rules.IPDestPushingRule import IPDestPushingRule
from src.SDM.util import bytes_to_ipv4


class BWMiddleWare(MiddleWare):
    def __init__(self, ovs_switch, controller_ip="127.0.0.1", switch_ip=None, controller_port=6633, switch_port=None,
                 protocols=None):
        super(BWMiddleWare, self).__init__(ovs_switch, controller_ip, switch_ip, controller_port, switch_port,
                                           protocols)
        self.frontier_default_value = {'duration': 0.0, 'byte_count': 0}
        self.logger = logging.getLogger(__name__)
        self.logger.info("Created BWMiddleWare")

    def handle_results(self, res, rule):
        if not res:
            return
        stat = {}
        res = res.replace('\r', ' ').replace('\n', ' ').replace(',', ' ').split(' ')
        res = [x for x in res if "=" in x]
        for r in res:
            stat[r.split('=')[0]] = r.split('=')[1]
        self.logger.info('rule                               '
                         'current bandwidth  duration           bytes')
        self.logger.info('---------------------------------- '
                         '------------------ ------------------ --------')
        try:
            new_byte_count = int(stat["n_bytes"]) - self.frontier_values[rule]['byte_count']
            new_duration = float(stat["duration"].split('s')[0]) - self.frontier_values[rule]['duration']
            current_rate = new_byte_count / new_duration
            self.frontier_values[rule] = {'duration': float(stat["duration"].split('s')[0]),
                                          'byte_count': int(stat["n_bytes"])}
        except ZeroDivisionError:
            if int(stat["n_bytes"]) == 0:
                self.logger.info('%34s %018.9f %018.9f %08d',
                                 rule,
                                 float("nan"),
                                 0,
                                 0)
                self.logger.info('Keeping the rule %s for monitoring, not enough data received', rule)
                self.keep_monitoring_level(rule)
                return
            else:
                current_rate = float("inf")
        except:
            self.logger.info('Error res %s', res)
            self.logger.info('Error stat %s', stat)
            raise

        self.logger.info('%34s %018.9f %018.09f %08d',
                         rule,
                         current_rate,
                         new_duration,
                         new_byte_count)
        self.handle_rule_stat(rule, current_rate)


    def create_rule(self, ip_addr, mask):
        return IPDestPushingRule(self.ovs_switch, self.datapath, ip_addr, mask, 1, 0, None, self.protocol_str)


    def handle_raw_msg(self, data):
        hex_data = ':'.join('{:02x}'.format(x) for x in data)
        if len(data) != 0:
            if hex_data.split(":")[1] == "0e" and hex_data.split(":")[24] == "01":
                ip_addr = bytes_to_ipv4(str(data[62:66]))
                mask = bytes_to_ipv4(str(data[66:70]))
                self.logger.debug("ip_bytes %s | mask_bytes %s", ':'.join('{:02x}'.format(x) for x in data[62:66]),
                                  ':'.join('{:02x}'.format(x) for x in data[66:70]))
                self.logger.debug("Monitoring %s:%s", ip_addr, mask)
                self.monitor(ip_addr, mask)
            return data
        else:
            return None


    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def get_rule_threshold(self, rule):
        return 1500000
