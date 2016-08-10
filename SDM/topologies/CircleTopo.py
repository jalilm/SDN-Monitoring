import random

from mininet.topo import Topo

from SDM import irange


class CircleTopo(Topo):
    """
    A circle Topology.
    Due to Mininet current implementation, this topology does
    not create two links between s1 and s2 when k=2, but rather
    one link only.
    """

    def __init__(self, k=1):
        super(CircleTopo, self).__init__()
        random_generator = random.Random()
        random_generator.seed()
        switches = []
        for i in irange(1, k):
            switches.append(self.addSwitch('s%s' % i))
            self.addLink(switches[i - 1], self.addHost('h%s' % i))
        random.shuffle(switches)
        for i in irange(1, k):
            self.addLink(switches[i - 1], switches[i % k])