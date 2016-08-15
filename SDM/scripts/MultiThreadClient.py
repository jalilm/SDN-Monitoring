#!/usr/bin/env python

"""
A host program.
"""

import mmap
import random
import socket
import sys
import time

from SDM.scripts.MyThread import MyThread
from SDM.util import get_dirs, get_params


class ClientThread(MyThread):
    """
    A class representing a host client thread.
    """

    def __init__(self, client_id, name, others, logs_dir_path, params):
        super(ClientThread, self).__init__(client_id, name, "client",
                                           logs_dir_path)
        self.others = others
        self.params = params
        self.random_generator = random.Random()
        self.random_generator.seed(name)

    def run(self):
        with open(self.params['General']['fileToSendPath'], 'r+b') as my_file:
            file_to_send = mmap.mmap(my_file.fileno(), 0)
        if len(self.others) == 0:
            self.log('No Others - exiting')
            return
        random_others = self.others[:]
        random.shuffle(random_others)
        num_connections = self.random_generator.randint(1,
                                                        self.params['Client']['maxConnections'])
        self.log('Choose to make: ' + str(num_connections) + ' connections.')
        for i in range(1, num_connections + 1):
            host = random_others[self.random_generator.randint(0,
                                                               len(random_others) - 1)]
            delay = self.random_generator.random() * \
                    self.params['Client']['maxSleepDelay']
            self.log('Sleeping for: ' + str(delay) + ' seconds')
            time.sleep(delay)
            start = self.random_generator.randint(0,
                                                  file_to_send.size() - 2)
            end = self.random_generator.randint(start + 1, file_to_send.size() - 1)
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, self.params['Server']['port']))
                self.log('Connection number ' + str(i))
                self.log('Connected to: ' + str(host) + ':' +
                         str(self.params['Server']['port']))
                sock.sendall(file_to_send[start:end])
                self.log('Sent all to: ' + str(host) + ':' +
                         str(self.params['Server']['port']) +
                         ' from ' + str(start) + ' to ' + str(end))
            except Exception, exception:
                self.log('Error: could not connect to ' + str(host) + ': ' +
                         str(exception))
            finally:
                sock.close()

        self.log('Finished Connections - exiting')


def main(argv):
    """
    The main code that calls the multi-thread client generating on-off traffic.
    """

    directories = get_dirs()
    params = get_params(directories)

    log_dir = directories['log']
    client_log_file = log_dir + 'client_' + argv[0] + '_log'

    number_of_threads = params['Client']['numberOfThreads']

    ip_prefix = params['General']['ipBase'].split(".")[0:3]
    ip_prefix = ip_prefix[0] + '.' + ip_prefix[1] + '.' + ip_prefix[2] + '.'

    others = []

    for i in range(1, int(argv[1]) + 1):
        if i != int(argv[0]):
            others.append(ip_prefix + str(i))

    with open(client_log_file, 'a') as _file:
        _file.write(str(time.time()) + ' ' + str(others) + '\n')
        _file.write(str(time.time()) + ' Spawning ' + str(number_of_threads) +
                    ' threads\n')

    threads = [ClientThread(int(argv[0]), 'Thread_' + str(i),
                            others, log_dir, params)
               for i in range(1, number_of_threads + 1)]
    random.shuffle(threads)

    for thread in threads:
        thread.start()

    with open(client_log_file, 'a') as _file:
        _file.write(str(time.time()) + ' Joined ' +
                    str(number_of_threads) + ' threads\n')

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main(sys.argv[1:])
