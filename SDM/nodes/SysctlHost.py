from mininet.node import Node


class SysctlHost(Node):
    def __init__(self, name, **params):
        super(SysctlHost, self).__init__(name, True, **params)
        self.cmd('sysctl -p')

    def stopwaiting(self):
        self.waiting = False
