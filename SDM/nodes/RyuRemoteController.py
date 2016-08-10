from mininet.log import error
from mininet.node import Controller


class RyuRemoteController(Controller):
    # noinspection PyPep8Naming
    def __init__(self, name="c0", ip="127.0.0.1",
                 port=6633, *ryuArgs, **kwargs):
        """Init.
           name: name to give controller
           ryuArgs: arguments (strings) to pass to RYU"""
        if not ryuArgs:
            ryuArgs = kwargs['ryuArgs']
            if not ryuArgs:
                error('error: no Ryu modules specified\n')
                return
        elif type(ryuArgs) not in ( list, tuple ):
            ryuArgs = [ryuArgs]

        super(RyuRemoteController, self).__init__(name=name,
                                                  command='ryu-manager',
                                                  cargs='--ofp-listen-host ' + ip + \
                                                        ' --ofp-tcp-listen-port %s' + \
                                                        ' --app-lists '.join(ryuArgs),
                                                  ip=ip,
                                                  port=port,
                                                  **kwargs)