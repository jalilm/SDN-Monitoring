import mmap

from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls

from SDM.apps.BaseController import BaseController

class PushingController(BaseController):
    def __init__(self, *args, **kwargs):
        super(PushingController, self).__init__(*args, **kwargs)
        self.alerts = []

    @set_ev_cls(ofp_event.EventOFPExperimenter, MAIN_DISPATCHER)
    def alert_handler(self, ev):
        msg = ev.msg
        if str(msg.data) in self.alerts:
            return
        self.info('Alert Received: %s', msg.data)
        self.alerts.append(str(msg.data))
        if len(self.alerts) == self.parameters['RunParameters']['numHH']:
            with open(self.parameters['General']['sharedMemFilePath'], "r+b") as _file:
                mem_map = mmap.mmap(_file.fileno(), 0)
                mem_map[:6] = self.parameters['General']['alertToken']
                mem_map.close()