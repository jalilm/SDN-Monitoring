from mininet.topo import Topo


class TraceTopology(Topo):
    def __init__(self):
        super(TraceTopology, self).__init__()
        switches = [self.addSwitch('s1')]
        self.addLink(switches[0], self.addHost('h1'))
        self.addLink(switches[0], self.addHost('h2'))
