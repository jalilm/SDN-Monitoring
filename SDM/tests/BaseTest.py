import logging
import os
from threading import Thread
from time import sleep

from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController

from SDM.nodes.SysctlHost import SysctlHost
from SDM.util import get_class


class BaseTest(object):
    """
    Base class used to provide a test infrastructure for more complicated test.
    """

    def __init__(self, shared_mem, directories, parameters):
        self.shared_mem_fd = shared_mem
        self.directories = directories
        self.parameters = parameters
        self.logger = logging.getLogger()
        self.topology = None
        self.net = None

    def setup_topology(self):
        """
        Used to initialize self.topology according to the test scenario.
        """
        topology_class = get_class(self.parameters['RunParameters']['topologyType'])
        try:
            topology = topology_class(k=self.parameters['RunParameters']['numberOfStations'])
            self.logger.debug("Setting up topology type: %s with %s stations",
                              self.parameters['RunParameters']['topologyType'],
                              self.parameters['RunParameters']['numberOfStations'])
        except TypeError:
            topology = topology_class()
            self.logger.debug("Setting up topology type: %s.", self.parameters['RunParameters']['topologyType'])
        return topology

    def setup_net(self):
        """
        Used to initialize self.net according to the test scenario.
        """
        self.logger.debug("Setting up mininet")
        try:
            switch = get_class(self.parameters['RunParameters']['mininet_switch'])
        except KeyError:
            switch = OVSSwitch
        return Mininet(self.topology, switch=switch,
                       controller=RemoteController,
                       host=SysctlHost,
                       build=False, xterms=self.parameters['General']['xterms'],
                       cleanup=self.parameters['General']['cleanup'],
                       ipBase=self.parameters['General']['ipBase'],
                       inNamespace=self.parameters['General']['inNameSpace'],
                       autoSetMacs=self.parameters['General']['autoSetMacs'],
                       autoStaticArp=self.parameters['General']['autoStaticArp'],
                       autoPinCpus=self.parameters['General']['autoPinCpus'],
                       listenPort=self.parameters['General']['listenPort'])

    def prepare_before_run(self):
        self.logger.debug("prepare_before_run")
        self.topology = self.setup_topology()
        self.net = self.setup_net()

    def detect_alert(self, target_func=None):
        if not target_func:
            target = BaseTest.detect
        else:
            target = target_func
        t = Thread(target=target, args=(self,))
        t.daemon = True
        t.start()

    def detect(self):
        time_step = self.parameters['RunParameters']['timeStep']
        start_token = self.parameters['General']['startGenerationToken']
        alert_token = self.parameters['General']['alertToken']
        while str(self.shared_mem_fd[:6]) == start_token:
            sleep(time_step)
        if str(self.shared_mem_fd[:6]) == alert_token:
            self.net.get('h1').stopwaiting()
            self.net.get('h2').stopwaiting()
            self.net.stop()

    def clean_after_run(self):
        self.logger.debug("clean_after_run")
        sdm_log_file = self.parameters['General']['SDMLogFile']
        con_log_file = self.parameters['General']['ControllerLogFile']
        output_log_file = self.directories['log'] + self.parameters['RunParameters']['mechanism'] + '-' + \
                          self.parameters['RunParameters']['state'] + '-' + \
                          self.parameters['RunParameters']['rate_type'] + '-' + \
                          self.parameters['RunParameters']['direction'] + '/' + \
                          str(self.parameters['RunParameters']['timeStep']) + '-' + \
                          str(self.parameters['RunParameters']['numHH']) + '-' + \
                          str(self.parameters['RunParameters']['common_mask']) + '-' + \
                          str(self.parameters['RunParameters']['k']) + '-' + \
                          str(self.parameters['RunParameters']['counters']) + \
                          '.log'

        os.system("cat " + con_log_file + + sdm_log_file + " | sort -n -s > " + output_log_file)
        os.system("rm /tmp/c0.log")
        os.system("rm " + sdm_log_file)

    # noinspection PyUnusedLocal
    def run(self):
        raise NotImplementedError
