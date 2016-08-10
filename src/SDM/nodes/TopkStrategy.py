import logging
import mmap

from src.SDM.nodes.Strategy import Strategy
from src.SDM.util import *


class TopkStrategy(Strategy):
    def __init__(self, k, counters, first_monitoring_table_id=1):
        super(TopkStrategy, self).__init__(first_monitoring_table_id)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("TopkStrategy")
        self.k = k
        self.counters = counters
        self.alert = False
        self.frontier_default_value = {'duration': 0.0000000001, 'byte_count': 0}
        self.current_depth = int(math.log(self.counters, 2))

    def handle_rule(self, rule, current_stat):
        self.logger.debug('Handling Rule %s', rule)
        self.logger.debug('status: %s', self.round_status)
        self.round_status[rule] = True
        self.logger.debug('status: %s', self.round_status)
        if not self.received_all_replys():
            self.logger.debug('not 2k yet')
            return
        self.logger.debug('Sorting')
        sorted_frontier = sorted(self.frontier_values.items(), key=lambda x: x[1]['byte_count'] / x[1]['duration'],
                                 reverse=True)

        skip_epoch = True
        for i in range(0, self.counters):
            if sorted_frontier[i][1]['byte_count']/sorted_frontier[i][1]['duration'] != 0:
                skip_epoch = False
                break

        if skip_epoch:
            self.logger.debug('We have only zero flows, skipping epoch and keeping all!')
            for j in range(0, self.counters):
                self.keep_monitoring_level(sorted_frontier[j][0])
            return

        self.current_depth += 1
        for i in range(0, self.counters / 2):
            self.info("JALIL: calling increase for %s", sorted_frontier[i][0])
            if self.increase_monitoring_level(sorted_frontier[i][0]):
                self.logger.debug('Finer monitoring rules for %s were added', sorted_frontier[i][0])
            else:
                self.alert = True

        if self.alert:
            self.issue_alert(sorted_frontier)
        else:
            self.info('Top ' + str(self.counters / 2) + ' for this epoch:')
            for i in range(0, self.counters / 2):
                self.info('%s) %s : %s', i + 1, sorted_frontier[i][0],
                          sorted_frontier[i][1]['byte_count'] / sorted_frontier[i][1]['duration'])

            for i in range(0, self.counters):
                self.remove_rule(sorted_frontier[i][0])
                self.info('Removed monitoring rule for %s', sorted_frontier[i][0])

    def issue_alert(self, sorted_frontier):
        self.info('Alert!')
        for i in range(0, self.k):
            self.info('Final Top %s', sorted_frontier[i][0].ipv4_string)
        with open(self.parameters['General']['sharedMemFilePath'], "r+b") as _file:
            mem_map = mmap.mmap(_file.fileno(), 0)
            mem_map[:6] = self.parameters['General']['alertToken']
            mem_map.close()

    def remove_rule(self, rule):
        rule.remove_flow()
        self.frontier_values.pop(rule, None)
