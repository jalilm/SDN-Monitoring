
import math
import os
import stat
from random import randint

from SDM.tests.TraceTest import TraceTest


class TopKTest(TraceTest):
    """
        A class that runs a single switch with 2 hosts, that
        sends a random portion of previously captured traces for
        top-k detection.
    """

    def __init__(self, shared_mem, directories, parameters):
        super(TopKTest, self).__init__(shared_mem, directories, parameters)
        self.random_second = -1

    def prepare_before_run(self):
        super(TopKTest, self).prepare_before_run()
        minimal_length_of_trace = self.parameters['RunParameters']['timeStep'] * (
            32 - math.log(self.parameters['RunParameters']['counters'], 2))
        trace_rate = 153 / (2 * self.parameters['RunParameters']['timeStep'] + minimal_length_of_trace +
                            5 * self.parameters['RunParameters']['timeStep'])
        self.random_second = "%02d" % randint(0, 59)
        trace_file = self.directories[
                         'home'] + "CAIDA-DLT/sec" + self.random_second + "/sec" + self.random_second + ".pcap"
        with open(self.parameters['RunParameters']['attack'], "w+") as f:
            f.write("# !/bin/bash\n")
            f.write("tcpreplay -M " + str(trace_rate) + " -i h1-eth0 " + trace_file + "\n")

        st = os.stat(self.parameters['RunParameters']['attack'])
        os.chmod(self.parameters['RunParameters']['attack'], st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def clean_after_run(self):
        super(TopKTest, self).clean_after_run()
        output_log_file = self.directories['log'] + self.parameters['RunParameters']['mechanism'] + '-' + \
                           self.parameters['RunParameters']['state'] + '-' + \
                           self.parameters['RunParameters']['rate_type'] + '-' + \
                           self.parameters['RunParameters']['direction'] + '/' + \
                           str(self.parameters['RunParameters']['timeStep']) + '-' + \
                           str(self.parameters['RunParameters']['numHH']) + '-' + \
                           str(self.parameters['RunParameters']['common_mask']) + '-' + \
                           str(self.parameters['RunParameters']['k']) + '-' + \
                           str(self.parameters['RunParameters']['counters']) + \
                           '.log'
        found_top_k_file = self.directories['log'] + self.parameters['RunParameters']['mechanism'] + '-' + \
                           self.parameters['RunParameters']['state'] + '-' + \
                           self.parameters['RunParameters']['rate_type'] + '-' + \
                           self.parameters['RunParameters']['direction'] + '/found_top' + \
                           str(self.parameters['RunParameters']['k']) + '_by_' + \
                           str(self.parameters['RunParameters']['counters']) + '_counters'

        true_top_k_file = self.directories['log'] + self.parameters['RunParameters']['mechanism'] + '-' + \
                          self.parameters['RunParameters']['state'] + '-' + \
                          self.parameters['RunParameters']['rate_type'] + '-' + \
                          self.parameters['RunParameters']['direction'] + '/true_top' + \
                          str(self.parameters['RunParameters']['k'])

        os.system("cat " + output_log_file + " | grep \"Final Top\" | cut -d\" \" -f4 | head -n " +
                  str(self.parameters['RunParameters']['k']) + " | sort > " + found_top_k_file)

        os.system("cat " + self.directories['home'] + 'CAIDA-DLT/sec' + str(self.random_second) + "/sec" +
                  str(self.random_second) + ".stat" + " | head -n " + str(self.parameters['RunParameters']['k']) +
                  " | cut -d\" \" -f1 | sort > " + true_top_k_file)
        res_file = self.directories['log'] + self.parameters['RunParameters']['mechanism'] + '-' + \
                   self.parameters['RunParameters']['state'] + '-' + \
                   self.parameters['RunParameters']['rate_type'] + '-' + \
                   self.parameters['RunParameters']['direction'] + '-' + \
                   str(self.parameters['RunParameters']['timeStep']) + '-' + \
                   str(self.parameters['RunParameters']['numHH']) + '-' + \
                   str(self.parameters['RunParameters']['common_mask'])
        os.system("echo -n " + str(self.parameters['RunParameters']['k']) + " " +
                  str(self.parameters['RunParameters']['counters']) + ": " + " >> " + res_file)
        os.system("comm -12 " + found_top_k_file + " " + true_top_k_file + " | wc -l >> " + res_file)
