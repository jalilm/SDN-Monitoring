from src.SDM.util import irange
from mininet.topo import Topo

BASE_MAC = '6a:bc:af:76:'

class ThreeCycleTopo(Topo):
    def __init__(self):
        super(ThreeCycleTopo, self).__init__()
        switches = []
        for i in irange(1, 3):
            switches.append(self.addSwitch('s%s' % i))
            for j in irange(1, 3):
                sub_switch = self.addSwitch('s%s-%s' % (i, j))
                self.addLink(sub_switch, self.addHost('h%s-%s' % (i, j), ip='10.0.%s.%s' % (i, j)))
                self.addLink(switches[i - 1], sub_switch, params1={'mac': BASE_MAC + '0%0d:%0d%0d' % (i, i, j)})
        self.addLink(switches[0], switches[1], 12, 21, params1={'mac': BASE_MAC + '01:02'},
                     params2={'mac': BASE_MAC + '02:01'})
        self.addLink(switches[0], switches[2], 13, 31, params1={'mac': BASE_MAC + '01:03'},
                     params2={'mac': BASE_MAC + '03:01'})
        self.addLink(switches[1], switches[2], 23, 32, params1={'mac': BASE_MAC + '02:03'},
                     params2={'mac': BASE_MAC + '03:02'})