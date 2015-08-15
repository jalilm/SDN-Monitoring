import logging
from time import sleep
from threading import Thread
import os

from src.SDM.nodes.SysctlHost import SysctlHost
from src.SDM.util import get_class, get_dirs, get_params
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController


class BaseTest(object):
    """
    Base class used to provide a test infrastructure for more complicated test.
    """

    def __init__(self, shared_mem, directories, params):
        self.shared_mem_fd = shared_mem
        self.directories = directories
        self.params = params
        self.logger = logging.getLogger(__name__)
        self.topo = None
        self.net = None

    def setup_topo(self):
        """
        Used to initialize self.topo according to the test scenario.
        """
        topo_class = get_class(self.params['RunParameters']['topoType'])
        try:
            topo = topo_class(k=self.params['RunParameters']['numberOfStations'])
            self.logger.debug("Setting up topo type: %s with %s stations", self.params['RunParameters']['topoType'],
                              self.params['RunParameters']['numberOfStations'])
        except TypeError:
            topo = topo_class()
            self.logger.debug("Setting up topo type: %s.", self.params['RunParameters']['topoType'])
        return topo

    def setup_net(self):
        """
        Used to initialize self.net according to the test scenario.
        """
        self.logger.debug("Setting up mininet")
        try:
            switch = get_class(self.params['RunParameters']['mininet_switch'])
        except KeyError:
            switch = OVSSwitch
        return Mininet(self.topo, switch=switch,
                       controller=RemoteController,
                       host=SysctlHost,
                       build=False, xterms=self.params['General']['xterms'],
                       cleanup=self.params['General']['cleanup'],
                       ipBase=self.params['General']['ipBase'],
                       inNamespace=self.params['General']['inNameSpace'],
                       autoSetMacs=self.params['General']['autoSetMacs'],
                       autoStaticArp=self.params['General']['autoStaticArp'],
                       autoPinCpus=self.params['General']['autoPinCpus'],
                       listenPort=self.params['General']['listenPort'])

    def prepare_before_run(self):
        self.logger.debug("prepare_before_run")
        self.topo = self.setup_topo()
        self.net = self.setup_net()
        pass

    def detect_alert(self, target_func=None):
        if not target_func:
            target = BaseTest.detect
        else:
            target = target_func
        t = Thread(target=target, args=(self,))
        t.daemon = True
        t.start()

    def detect(self):
        time_step = self.params['RunParameters']['timeStep']
        start_token = self.params['General']['startGenerationToken']
        alert_token = self.params['General']['alertToken']
        while str(self.shared_mem_fd[:6]) == start_token:
            sleep(time_step)
        if str(self.shared_mem_fd[:6]) == alert_token:
            self.net.get('h1').stopWaiting()
            self.net.stop()

    def clean_after_run(self):
        self.logger.debug("clean_after_run")
        dirs = get_dirs()
        params = get_params(dirs)
        sdm_log_file = dirs['log'] + '/SDM.log'
        output_log_file = dirs['log'] + '/' + params['RunParameters']['state'] + '-' + params['RunParameters'][
            'rate_type'] + '-' + params['RunParameters']['direction'] + '/' + str(
            params['RunParameters']['timeStep']) + '-' + str(
            params['RunParameters']['numHH']) +'.log'

        os.system("cat /tmp/c0.log " + sdm_log_file + " | sort -n -s > " + output_log_file)
        os.system("rm /tmp/c0.log")
        os.system("rm " + sdm_log_file)


def run(self):
    assert False
