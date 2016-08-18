from SDM.nodes.DoubleKStrategy import DoubleKStrategy


# noinspection PyAbstractClass
class InnerDoubleKStrategy(DoubleKStrategy):
    def __init__(self, k, counters, first_monitoring_table_id=1):
        super(InnerDoubleKStrategy, self).__init__(k, counters, first_monitoring_table_id)
        self.logger.debug("DoubleKStrategy")
        self.previous_frontier_stats = {}
        self.frontier_stats = {}
        self.first_inner_epoch = True
        self.stability_threshold = self.parameters['RunParameters']['stability_threshold']

    def handle_rule(self, rule, current_stat):
        self.logger.debug('Handling Rule %s', rule)
        self.round_status[rule] = True
        if self.first_inner_epoch:
            self.previous_frontier_stats[rule] = current_stat
        else:
            self.frontier_stats[rule] = current_stat
        if not self.received_all_replys():
            self.logger.debug('not 2k yet')
            return
        elif self.first_inner_epoch:
            self.logger.debug('Got 2k results of first inner epoch')
            for rule in self.frontier:
                self.keep_monitoring_level(rule)
            self.logger.debug('Keeping current frontier to allow another inner epoch')
            self.first_inner_epoch = False
            return

        self.logger.debug('Got 2k stats of not first inner epoch')

        self.logger.debug('Sorting')
        sorted_frontier = sorted(self.frontier_values.items(), key=lambda x: x[1], reverse=True)

        skip_epoch = True
        for i in range(0, self.counters):
            if sorted_frontier[i][1]['byte_count']/sorted_frontier[i][1]['duration'] != 0:
                skip_epoch = False
                break

        if skip_epoch:
            self.logger.debug('We have only zero flows, skipping epoch and keeping all!')
            for j in range(0, self.counters):
                rule = sorted_frontier[j][0]
                self.previous_frontier_stats[rule] = self.frontier_stats[rule]
                self.keep_monitoring_level(rule)
            return

        self.logger.debug('Checking if counters are stable')
        for rule, stat in self.frontier_stats.items():
            try:
                diff = (stat - self.previous_frontier_stats[rule]) / self.previous_frontier_stats[rule]
            except ZeroDivisionError:
                self.logger.debug('Rule %s have zero previous stat', rule)
                continue
            if diff > self.stability_threshold or diff < self.stability_threshold*-1:
                self.logger.info('Rule %s have diff %d while stability threshold is %d', rule, diff,
                                 self.stability_threshold)
                self.logger.info('Skipping epoch')
                skip_epoch = True
                break

        if skip_epoch:
            self.logger.debug('We have non stable rules, skipping inner epoch')
            for j in range(0, self.counters):
                rule = sorted_frontier[j][0]
                self.previous_frontier_stats[rule] = self.frontier_stats[rule]
                self.keep_monitoring_level(rule)
            return

        self.logger.debug('Counters are stable')

        self.current_depth += 1
        for i in range(0, self.counters / 2):
            self.logger.debug("Calling increase for %s", sorted_frontier[i][0])
            if self.increase_monitoring_level(sorted_frontier[i][0]):
                self.logger.debug('Finer monitoring rules for %s were added', sorted_frontier[i][0])
            else:
                self.alert = True

        if self.alert:
            self.issue_alert(sorted_frontier)
        else:
            self.logger.info('Top ' + str(self.counters / 2) + ' for this epoch:')
            for i in range(0, self.counters / 2):
                self.logger.info('%s) %s : %s', i + 1, sorted_frontier[i][0],
                                 sorted_frontier[i][1]['byte_count'] / sorted_frontier[i][1]['duration'])

            for i in range(0, self.counters):
                self.remove_rule(sorted_frontier[i][0])
                self.logger.info('Removed monitoring rule for %s', sorted_frontier[i][0])
