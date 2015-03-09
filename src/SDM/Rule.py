class Rule(object):
    """
    A class that represents a rule in the switch table.
    """

    def __init__(self, datapath, table_id, priority):
        self.datapath = datapath
        self.table_id = table_id
        self.priority = priority
        self.match = self.datapath.ofproto_parser.OFPMatch()

    def __str__(self):
        return self.match.__str__()

    def __hash__(self):
        """
        Hash value according to immutable ipv4_string and subnet_string.
        :return: hash value.
        """
        return self.match.__hash__()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        return isinstance(other, Rule) and self.match == other.match

    def get_match(self):
        """
        Used as C++ style copy constructor.
        Each rule should define its partial/full Copy Constructor of OFPMatch,
        due to bug that prohibits more than serialization of such object
        thus preventing saving the matches aside.
        """
        copy_match = self.datapath.ofproto_parser.OFPMatch()
        return copy_match

    def get_finer_rules(self):
        return self

    def next_table_id(self):
        return self.table_id + 1

    def remove_flow(self):
        mod = self.datapath.ofproto_parser.OFPFlowMod(
            datapath=self.datapath, command=self.datapath.ofproto.OFPFC_DELETE_STRICT, table_id=self.table_id,
            priority=self.priority, match=self.get_match())
        self.datapath.send_msg(mod)

    def add_flow(self, inst):
        mod = self.datapath.ofproto_parser.OFPFlowMod(datapath=self.datapath, table_id=self.table_id,
                                                      priority=self.priority,
                                                      match=self.match, instructions=inst)
        self.datapath.send_msg(mod)

    def add_flow_and_apply_actions(self, actions):
        ofproto = self.datapath.ofproto
        parser = self.datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        self.add_flow(inst)

    def add_flow_and_send_to_meter(self, meter_id, actions):
        ofproto = self.datapath.ofproto
        parser = self.datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions),
                parser.OFPInstructionMeter(meter_id)]
        self.add_flow(inst)

    def add_flow_and_goto_next_table(self, actions):
        ofproto = self.datapath.ofproto
        parser = self.datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions),
                parser.OFPInstructionGotoTable(self.next_table_id())]

        self.add_flow(inst)

    def add_meter_dscp(self, meter_id):
        ofproto = self.datapath.ofproto
        parser = self.datapath.ofproto_parser
        bands = [parser.OFPMeterBandDscpRemark(1, 1, 0, None, None)]
        meter_mod = parser.OFPMeterMod(self.datapath, meter_id=meter_id, bands=bands,
                                       flags=ofproto.OFPMF_PKTPS | ofproto.OFPMF_STATS)
        self.datapath.send_msg(meter_mod)