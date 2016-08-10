from datetime import datetime

from ryu.lib import hub

from src.SDM.apps.BaseController import BaseController


class PullingController(BaseController):
    def __init__(self, *args, **kwargs):
        super(PullingController, self).__init__(*args, **kwargs)
        self.monitor_threads = {}

    def after_datapaths_construction(self):
        for dp in self.datapaths:
            datapath = self.datapaths[dp]
            self.monitor_threads[datapath] = hub.spawn(self.monitor, datapath)

    def monitor(self, datapath):
        time_step_number = 0
        while True:
            hub.sleep(self.parameters['RunParameters']['timeStep'])
            time_step_number += 1
            self.info('')
            self.info('Time step #%d - ' + datetime.now().strftime('%H:%M:%S.%f'), time_step_number)
            self.info('Sending stats request: %016x', datapath.id)
            datapath.request_stats()
