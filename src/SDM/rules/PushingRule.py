import logging

from src.SDM.rules.Rule import Rule


class PushingRule(Rule):
    """
    A class that represents a rule in the switch table.
    """

    def __init__(self, switch, datapath, table_id=0, priority=0, father_rule=None, protocol="OpenFlow13"):
        super(PushingRule, self).__init__(datapath, table_id, priority, father_rule)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Created PushingRule")
        self.switch = switch
        self.match_args["priority"] = self.priority
        self.match = "table=%s,priority=%s" % (self.table_id, self.priority)
        self.protocol = protocol

    def __repr__(self):
        return "PushingRule(" + repr(self.switch) + ", " + repr(self.datapath) + ", " + repr(self.table_id) + \
               ", " + repr(self.priority) + ")"

    def __str__(self):
        return "PushingRule"

    def get_match(self, exculde=None):
        res = "table=%s" % self.table_id
        if not exculde:
            res = self.match
        else:
            for k, v in self.match_args.iteritems():
                if k not in exculde:
                    if v:
                        res += ",%s=%s" % (k, v)
                    else:
                        res += ",%s" % k
        self.logger.debug("get_match result = %s", res)
        return res

    def add_match_arg(self, key, value):
        self.match_args[key] = value
        if value:
            self.match += ",%s=%s" % (key, value)
        else:
            self.match += ",%s" % key

    def update_match(self):
        pass

    def remove_flow(self):
        self.logger.debug("Remove Flow")
        return self.switch.dpctl("--protocols %s --strict del-flows" % self.protocol, "%s" % self.get_match())

    def add_flow(self, inst):
        self.logger.debug("Add Flow")
        inst_str = "actions=%s" % inst
        return self.switch.dpctl("--protocols %s --strict add-flow" % self.protocol,
                                 "%s,%s" % (self.get_match(), inst_str))

    def add_flow_and_apply_actions(self, actions):
        self.add_flow(actions)

    def add_flow_and_goto_next_table(self, actions):
        self.logger.debug("Add Flow and Goto Next Table")
        inst_str = "resubmit\(,%s\)" % self.next_table_id()
        return self.add_flow(inst_str)

    def add_flow_and_send_to_meter(self, meter_id, actions):
        raise NotImplementedError

    def add_meter_dscp(self, meter_id):
        raise NotImplementedError

    def get_stats(self):
        self.logger.debug("Get Stats")
        self.logger.debug("--protocols %s dump-flows s1 %s" % (self.protocol, self.get_match(["priority"])))
        res = self.switch.dpctl("--protocols %s dump-flows" % self.protocol, "%s" % self.get_match(["priority"]))
        self.logger.debug("result: %s" % res)
        return res
