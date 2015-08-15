from datetime import datetime

from ryu.lib import hub
from src.SDM.apps.BaseController import BaseController


class PullingController(BaseController):
    def __init__(self, *args, **kwargs):
        super(PullingController, self).__init__(*args, **kwargs)
        self.monitor_thread = hub.spawn(self.monitor)

    def monitor(self):
        time_step_number = 0
        while True:
            hub.sleep(self.parameters['RunParameters']['timeStep'])
            time_step_number += 1
            self.info('')
            self.info('Time step #%d - ' + datetime.now().strftime('%H:%M:%S.%f'), time_step_number)
            for dp in self.datapaths:
                dpp = self.datapaths[dp]
                self.info('Sending stats request: %016x', dpp.id)
                dpp.request_stats()