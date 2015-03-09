import abc


class Datapath(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, datapath):
        # The order he is important
        self.datapath = datapath
        self.id = self.calc_id()

    def set_route_tables(self):
        pass

    def set_main_monitor_table(self):
        pass

    @abc.abstractmethod
    def calc_id(self):
        """
        This method is abstract and should be overriden at subclasses.
        Each Sub-Datapath should implement, how to calculate its id.
        """
        return