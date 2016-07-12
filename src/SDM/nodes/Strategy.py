from multiprocessing import Lock

from src.SDM.util import *


class Strategy(object):
    def __init__(self, first_monitoring_table_id=1):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Strategy")
        self.first_monitoring_table_id = first_monitoring_table_id
        self.root_rules = []
        self.frontier = []
        self.next_frontier = []
        self.frontier_values = {}
        self.frontier_default_value = 0
        self.frontier_locks = {}
        self.round_status = {}
        self.sibling_rule = {}

    def received_all_replys(self):
        for rule in self.frontier:
            if not self.round_status.has_key(rule):
                return False
        return True

    def increase_monitoring_level(self, rule):
        if rule.subnet_string == "255.255.255.255":
            self.next_frontier.append(self.get_original_rule(rule))
            return False  # Alert
        if rule not in self.frontier:
            self.logger.error("rule is not in subrules - 1")
            assert False
        with self.frontier_locks[rule]:
            if rule not in self.frontier:
                self.logger.error("rule is not in subrules - 2")
                assert False
            orig_rule = self.get_original_rule(rule)
            self.set_refined_monitoring_rules(orig_rule)
        return True

    def set_refined_monitoring_rules(self, rule):
        rules = rule.get_finer_rules()
        actions = []

        for r in rules:
            if r not in self.frontier:
                self.frontier_locks[r] = Lock()
                self.next_frontier.append(r)
                self.frontier_values[r] = self.frontier_default_value
                self.sibling_rule[r] = list(set(rules) - {r})
                r.add_flow_and_goto_next_table(actions)

        self.round_status[rule] = True

    def reduce_monitoring_level(self, rule):
        orig_rule = self.get_original_rule(rule)
        if orig_rule in self.root_rules:
            self.next_frontier.append(orig_rule)
            return False, "I'm root rule"
        if orig_rule not in self.frontier:
            self.logger.error("rule is not in subrules - 3")
            assert False

        with self.frontier_locks[orig_rule]:
            self.round_status[orig_rule] = False

        return self.remove_refined_monitoring_rules(orig_rule)

    def remove_refined_monitoring_rules(self, rule):
        sibling = self.sibling_rule[rule][0]

        with self.frontier_locks[sibling]:
            if sibling not in self.frontier:
                self.next_frontier.append(rule)
                return False, "waiting for bro children"
            if self.round_status[sibling]:
                self.next_frontier.append(rule)
                return False, "staying with bro"
            if self.round_status[sibling] is None:
                self.next_frontier.append(rule)
                return False, "waiting for bro"

        corase_rule = rule.get_coarse_rule()

        if corase_rule not in self.frontier:
            self.next_frontier.append(corase_rule)
            self.frontier_values[corase_rule] = self.frontier_default_value

        rule.remove_flow()
        sibling.remove_flow()
        assert sibling in self.next_frontier
        self.next_frontier.remove(sibling)
        self.frontier_values.pop(rule, None)
        self.frontier_values.pop(sibling, None)
        self.frontier_locks.pop(rule)
        self.frontier_locks.pop(sibling)
        return True, rule, sibling

    def keep_monitoring_level(self, rule):
        orig_rule = self.get_original_rule(rule)
        self.next_frontier.append(orig_rule)

    def get_original_rule(self, rule):
        for r in self.frontier:
            if r == rule:
                return r
        self.logger.error("rule is not original")
        assert False

    def request_stats(self):
        assert False

    def set_main_monitor_table(self):
        actions = []
        for rule in self.next_frontier:
            rule.add_flow_and_goto_next_table(actions)
            self.round_status[rule] = 0

    def add_monitoring_rule(self, rule):
        self.root_rules.append(rule)
        self.next_frontier.append(rule)
        self.frontier_locks[rule] = Lock()
        self.frontier_values[rule] = self.frontier_default_value