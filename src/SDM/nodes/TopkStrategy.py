import mmap
from src.SDM.nodes.Strategy import Strategy
from src.SDM.util import *
from time import time


class TopkStrategy(Strategy):
    def __init__(self, k, first_monitoring_table_id=1):
        super(TopkStrategy, self).__init__(first_monitoring_table_id)
        self.logger = logging.getLogger(__name__)
        self.info("TopkStrategy")
        self.k = k
        self.alert = False
        self.frontier_default_value = {'duration': 0.0000000001, 'byte_count': 0}

    def info(self, msg, *args, **kwargs):
        self.logger.info(str(time()) + " " + msg, *args, **kwargs)

    def handle_rule(self, rule, current_stat):
        self.logger.debug('Handling Rule %s', rule)
        with self.frontier_locks[rule]:
            self.logger.debug('status: %s', self.round_status)
            self.round_status[rule] = True
            self.logger.debug('status: %s', self.round_status)
            if not self.received_all_replys():
                self.logger.debug('not 2k yet')
                return
            self.logger.debug('Sorting')
            sorted_frontier = sorted(self.frontier_values.items(), key=lambda x: x[1]['byte_count']/x[1]['duration'], reverse=True)

        skip_epoch = True
        for i in range(0, 2*self.k):
            if sorted_frontier[i][1]['byte_count']/sorted_frontier[i][1]['duration'] != 0:
                skip_epoch = False
                break

        if skip_epoch:
            self.logger.debug('We have 2*k zero flows, skipping epoch and keeping all!')
            for j in range(0, 2 * self.k):
                self.keep_monitoring_level(sorted_frontier[j][0])
            return

        for i in range(0,self.k):
            if self.increase_monitoring_level(sorted_frontier[i][0]):
                self.info('Finer monitoring rules for %s were added', sorted_frontier[i][0])
            else:
                self.alert()
            self.info('%s) %s : %s', i + 1, sorted_frontier[i][0],
                      sorted_frontier[i][1]['byte_count'] / sorted_frontier[i][1]['duration'])

        for i in range(0, 2*self.k):
            self.remove_rule(sorted_frontier[i][0])
            self.info('Removed monitoring rule for %s', sorted_frontier[i][0])

    def alert(self):
        self.alert = True
        self.info('Alert!')
        with open(self.parameters['General']['sharedMemFilePath'], "r+b") as _file:
            mem_map = mmap.mmap(_file.fileno(), 0)
            mem_map[:6] = self.parameters['General']['alertToken']
            mem_map.close()

    def remove_rule(self, rule):
        rule.remove_flow()
        self.frontier_values.pop(rule, None)
