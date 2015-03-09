import abc

from src.SDM.SysctlHost import SysctlHost
from src.SDM.ConnectedTopo import ConnectedTopo
from src.SDM.BinaryTreeTopo import BinaryTreeTopo
from src.SDM.RandomTreeTopo import RandomTreeTopo
from src.SDM.CircleTopo import CircleTopo
from mininet.net import Mininet
from mininet.topo import LinearTopo
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
        # Assignment is not really needed, just to avoid pylint complaints.
        self.topo = self.setup_topo()
        self.net = self.setup_net()

    def setup_topo(self):
        """
        Used to initialize self.topo according ot the test scenario.
        """
        topo_type = self.params['RunParameters']['topoType']
        if topo_type == 'linear':
            self.topo = LinearTopo(k=self.
                                   params['RunParameters']['numberOfStations'])
        elif topo_type == 'binaryTree':
            self.topo = BinaryTreeTopo(k=self.
                                       params['RunParameters']['numberOfStations'])
        elif topo_type == 'randomTree':
            self.topo = RandomTreeTopo(k=self.
                                       params['RunParameters']['numberOfStations'])
        elif topo_type == 'circle':
            self.topo = CircleTopo(k=self.
                                   params['RunParameters']['numberOfStations'])
        elif topo_type == 'connected':
            self.topo = ConnectedTopo(k=self.
                                      params['RunParameters']['numberOfStations'])
        else:
            self.topo = None
        return self.topo


    def setup_net(self):
        """
        Used to initialize self.net according to the test scenario.
        """
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
        #self.net.addController(RemoteController
        #                       ('c0', self.params['General']['controllerIP'],
        #                        self.params['General']['controllerPort']))
        return self.net

    def merge_logs(self):
        pass

    @abc.abstractmethod
    def run(self):
        """
        each subclass should override this function.
        """
        return
