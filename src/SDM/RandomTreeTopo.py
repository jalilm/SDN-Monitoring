import random

from src.SDM.util import irange
from mininet.topo import Topo


class RandomTreeTopo(Topo):
    """
    Topology for a random tree (connected acyclic graph) network where hosts are at every level.
    """

    def __init__(self, k=1):
        super(RandomTreeTopo, self).__init__()
        random_generator = random.Random()
        random_generator.seed()
        switches = []
        num_links = k - 1
        current_switch = 0
        for i in irange(1, k):
            switches.append(self.addSwitch('s%s' % i))
            self.addLink(switches[i - 1], self.addHost('h%s' % i))
        random.shuffle(switches)
        while num_links > 0:
            current_fanout = random_generator.randint(1, num_links)
            for _ in irange(1, current_fanout):
                self.addLink(switches[current_switch], switches[k - num_links])
                num_links -= 1
            current_switch += 1