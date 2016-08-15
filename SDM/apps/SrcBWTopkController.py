import math
from datetime import datetime

from ryu.lib import hub

from SDM.apps.SrcBWPullingController import SrcBWPullingController


class SrcBWTopkController(SrcBWPullingController):
    def __init__(self, *args, **kwargs):
        super(SrcBWTopkController, self).__init__(*args, **kwargs)
        assert (math.log(self.parameters['RunParameters']['counters'], 2) % 1 == 0)
        self.k = self.parameters['RunParameters']['k']
        self.counters = self.parameters['RunParameters']['counters']

    def handle_rule_stat(self, rule, current_stat, main_datapath):
        main_datapath.handle_rule(rule, current_stat)

    def monitor(self, datapath):
        time_step_number = 0
        log_counters = int(math.log(self.counters, 2))
        ts = self.parameters['RunParameters']['timeStep']
        minimal_ts = 2
        maximal_ts = 2 * ts - minimal_ts
        total_depth = 32 - log_counters
        ts_delta = (maximal_ts - minimal_ts) / total_depth
        while True:
            for dp in self.datapaths:
                current_depth = datapath.current_depth - log_counters
                if self.parameters['RunParameters']['tempStepChange'] == "normal":
                    sleep_time = ts
                elif self.parameters['RunParameters']['tempStepChange'] == "negative":
                    sleep_time = maximal_ts - (1 + current_depth) * ts_delta
                elif self.parameters['RunParameters']['tempStepChange'] == "positive":
                    sleep_time = minimal_ts + (1 + current_depth) * ts_delta
                elif self.parameters['RunParameters']['tempStepChange'] == "posneg":
                    if current_depth <= total_depth / 2 + 1:
                        sleep_time = minimal_ts + current_depth * (ts_delta * 2)
                    else:
                        sleep_time = maximal_ts - (current_depth - (total_depth / 2 + 1)) * (ts_delta * 2)

                self.info('Sleeping for %f', sleep_time)
                hub.sleep(sleep_time)
                time_step_number += 1
                self.info('')
                self.info('Time step #%d - ' + datetime.now().strftime('%H:%M:%S.%f'), time_step_number)
                dpp = self.datapaths[dp]
                self.info('Sending stats request: %016x', dpp.id)
                dpp.request_stats()
