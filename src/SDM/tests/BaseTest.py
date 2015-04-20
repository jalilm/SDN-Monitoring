import abc
import logging

from src.SDM.nodes import SysctlHost
from src.SDM.util import get_class
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController


class BaseTest(object):
    """
    Base class used to provide a test infrastructure for more complicated test.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, shared_mem, directories, params):
        self.shared_mem_fd = shared_mem
        self.directories = directories
        self.params = params
        self.logger = logging.getLogger(__name__)
        # Assignment is not really needed, just to avoid pylint complaints.
        self.topo = self.setup_topo()
        self.net = self.setup_net()

    def setup_topo(self):
        """
        Used to initialize self.topo according ot the test scenario.
        """

        self.logger.debug("Setting up topo type: %s with %s stations", self.params['RunParameters']['topoType'],
                          self.params['RunParameters']['numberOfStations'])
        topo_class = get_class(self.params['RunParameters']['topoType'])
        self.topo = topo_class(k=self.params['RunParameters']['numberOfStations'])

    def setup_net(self):
        """
        Used to initialize self.net according to the test scenario.
        """
        self.logger.debug("Setting up mininet")
        self.net = Mininet(self.topo, switch=OVSSwitch,
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
        return self.net

    def prepare_before_run(self):
        self.logger.debug("prepare_before_run")
        pass

    def clean_after_run(self):
        self.logger.debug("clean_after_run")
        pass

    @abc.abstractmethod
    def run(self):
        """
        each subclass should override this function.
        """
        return
