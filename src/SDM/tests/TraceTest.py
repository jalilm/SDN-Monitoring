import os
from time import sleep, strftime, localtime
import logging
from src.SDM.nodes.RyuRemoteController import RyuRemoteController
from src.SDM.tests.BaseTest import BaseTest
from src.SDM.topologies.TraceTopo import TraceTopo
from src.SDM.util import get_dirs, get_params


class TraceTest(BaseTest):
    """
    A class that runs a single switch with 2 hosts, that
    sends previously captured traces.
    """

    def __init__(self, shared_mem, directories, params):
        super(TraceTest, self).__init__(shared_mem, directories, params)
        self.logger = logging.getLogger(__name__)

    def setup_topo(self):
        self.logger.debug("setup_topo")
        return TraceTopo()

    def setup_net(self):
        self.logger.debug("setup_net")
        net = super(TraceTest, self).setup_net()
        net.addController(RyuRemoteController(name="c0", ip=self.params['General']['controllerIP'],
                                              port=self.params['General']['controllerPort'],
                                              ryuArgs=["",
                                                       self.params['RunParameters']['ryuApps']]))
        return net

    def run(self):
        """
        Executes the test and Mininet and the tcpreplay.
        """
        self.logger.info("run")
        self.net.build()
        self.net.interact()
        return
        self.logger.debug("starting the net")
        self.net.start()

        # TODO: delay used to allow completion of the handshake,
        # check if we can get rid of it.
        self.logger.debug("sleeping got 10 sec")
        sleep(10)

        host1 = self.net.get('h1')
        # TODO: Sending 5 minutes data - Fix me!
        self.logger.info(strftime(" - %H:%M:%S ", localtime()) +  "Started sending traces from h1")
        host1.cmd('bash ~/SDN-Monitoring/trace_before')
        self.logger.info(strftime(" - %H:%M:%S ", localtime()) +"Attack started traces from h1")
        host1.cmd('bash ~/SDN-Monitoring/attack')
        self.logger.info(strftime(" - %H:%M:%S ", localtime()) +"Attack finished from h1")
        host1.cmd('bash ~/SDN-Monitoring/trace_after')
        self.logger.debug("Stopping the net")
        self.net.stop()

    def clean_after_run(self):
        self.logger.debug("clean_after_run")
        dirs = get_dirs()
        params = get_params(dirs)
        sdm_log_file = dirs['log'] + '/SDM.log'
        output_log_file = dirs['log'] + '/parameters' + str(params['RunParameters']['timeStep']) + '.log'
        os.system("cat /tmp/c0.log " + sdm_log_file+ " | sort -n -s > " + output_log_file)
        os.system("rm /tmp/c0.log")
        os.system("rm " + sdm_log_file)
