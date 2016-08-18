from datetime import datetime

from ryu.lib import hub

from SDM.apps.SrcBWDoubleKController import SrcBWDoubleKController


class SrcBWInnerDoubleKController(SrcBWDoubleKController):

    def __init__(self, *args, **kwargs):
        super(SrcBWInnerDoubleKController, self).__init__(*args, **kwargs)

    def monitor(self, datapath):
        time_step_number = 0
        ts = self.parameters['RunParameters']['timeStep']
        sleep_time = ts / self.parameters['RunParameters']['inner_epochs']
        while True:
            for dp in self.datapaths:
                self.logger.info('Sleeping for %f', sleep_time)
                hub.sleep(sleep_time)
                time_step_number += 1
                self.logger.info('Time step #%d - ' + datetime.now().strftime('%H:%M:%S.%f'), time_step_number)
                dpp = self.datapaths[dp]
                self.logger.info('Sending stats request: %016x', dpp.id)
                dpp.request_stats()
