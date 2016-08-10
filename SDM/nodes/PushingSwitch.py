from mininet.node import OVSSwitch


class PushingSwitch(OVSSwitch):
    def __init__(self, name, **params):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Created PushingSwitch")
        self.middlewares = []
        self.dirs = get_dirs()
        self.parameters = get_params(self.dirs)
        self.middleware_class = get_class(self.parameters['RunParameters']['middleware'])
        super(PushingSwitch, self).__init__(name, **params)

    def start(self, controllers):
        """Start up a new OVS OpenFlow switch using ovs-vsctl"""
        if self.inNamespace:
            raise Exception(
                'OVS kernel switch does not work in a namespace')
        int(self.dpid, 16)  # DPID must be a hex string
        # Command to add interfaces
        intfs = ''.join(' -- add-port %s %s' % ( self, intf ) +
                        self.intfOpts(intf)
                        for intf in self.intfList()
                        if self.ports[intf] and not intf.IP())
        # Command to create controller entries
        clist = [( self.name + c.name, '%s:%s:%d' %
                   ( 'tcp', "127.0.0.1", c.port + 1 ) )
                 for c in controllers]
        self.middlewares = [
            self.middleware_class(self, controller_ip=c.IP(), controller_port=c.port, protocols=self.protocols) for c in
            controllers]
        [m.start() for m in self.middlewares]
        if self.listenPort:
            clist.append(( self.name + '-listen',
                           'ptcp:%s' % self.listenPort ))
        ccmd = '-- --id=@%s create Controller target=\\"%s\\"'
        if self.reconnectms:
            ccmd += ' max_backoff=%d' % self.reconnectms
        cargs = ' '.join(ccmd % ( name, target )
                         for name, target in clist)
        # Controller ID list
        cids = ','.join('@%s' % name for name, _target in clist)
        # Try to delete any existing bridges with the same name
        if not self.isOldOVS():
            cargs += ' -- --if-exists del-br %s' % self
        # One ovs-vsctl command to rule them all!
        self.vsctl(cargs +
                   ' -- add-br %s' % self +
                   ' -- set bridge %s controller=[%s]' % ( self, cids  ) +
                   self.bridgeOpts() +
                   intfs)
        # If necessary, restore TC config overwritten by OVS
        if not self.batch:
            for intf in self.intfList():
                self.TCReapply(intf)
