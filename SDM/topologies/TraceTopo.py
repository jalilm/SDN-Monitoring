from mininet.topo import Topo


class TraceTopo(Topo):
    def __init__(self):
        super(TraceTopo, self).__init__()
        switches = [self.addSwitch('s1')]
        self.addLink(switches[0], self.addHost('h1'))
        self.addLink(switches[0], self.addHost('h2'))
