from mininet.topo import Topo


class SynTraceTopo(Topo):
    def __init__(self, k=1):
        super(SynTraceTopo, self).__init__()
        switches = [
            self.addSwitch('s1', protocols=["OpenFlow10,OpenFlow11,OpenFlow12,OpenFlow13,OpenFlow14,OpenFlow15"])]
        self.addLink(switches[0], self.addHost('h1'))
        self.addLink(switches[0], self.addHost('h2'))
