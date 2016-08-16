from mininet.topo import Topo

from SDM.util import irange


class BinaryTreeTopo(Topo):
    """
    Topology for a binary tree network where hosts are at every level
    """

    def __init__(self, k=1):
        super(BinaryTreeTopo, self).__init__()
        switches = []
        for i in irange(1, k):
            switches.append(self.addSwitch('s%s' % i))
            self.addLink(switches[i - 1], self.addHost('h%s' % i))
        for i in irange(0, k - 1):
            parent_index = (i - 1) / 2
            if parent_index >= 0:
                self.addLink(switches[parent_index], switches[i])
