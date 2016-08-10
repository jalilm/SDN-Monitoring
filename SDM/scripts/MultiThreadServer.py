#!/usr/bin/env python

"""
A server program.
"""

import Queue
import mmap
import random
import socket
import sys
import time

from SDM import MyThread
from SDM import get_dirs, get_params


class ServerThread(MyThread):
    """
    A server thread class.
    """

    def __init__(self, server_id, name, sockets_queue, logs_dir_path):
        super(ServerThread, self).__init__(server_id, name, "server",
                                           logs_dir_path)
        self.sockets_queue = sockets_queue

    def run(self):
        dirs = get_dirs()
        params = get_params(dirs)
        while True:
            client, address = self.sockets_queue.get()
            self.log('Got connection from' + str(address))
            data = True
            while data:
                data = client.recv(params['General']['recvSize'])
            client.close()
            self.log('Closed connection with ' + str(address))
            self.sockets_queue.task_done()


def main(argv):
    """
    The main code that launches a multi-threaded server.
    """
    who_am_i = argv[0]

    directories = get_dirs()
    params = get_params(directories)

    log_dir = directories['log']
    server_log_file = log_dir + 'server_' + who_am_i + '_log'
    number_of_threads = params['Server']['numberOfThreads']

    with open(params['General']['sharedMemFilePath'], "r+b") as _file:
        mem_map = mmap.mmap(_file.fileno(), 0)

    with open(server_log_file, 'a') as _file:
        _file.write(str(time.time()) + ' Spawning ' + str(number_of_threads) +
                    ' threads\n')

    sockets_queue = Queue.Queue()
    workers = [ServerThread(who_am_i, 'Thread_' + str(i), sockets_queue,
                            log_dir)
               for i in range(1, number_of_threads + 1)]
    random.shuffle(workers)

    _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _socket.settimeout(params['Server']['drainTimeout'])
    _socket.bind(('', params['Server']['port']))
    _socket.listen(socket.SOMAXCONN)

    for worker in workers:
        worker.daemon = True
        worker.start()

    mem_map.seek(0)
    while params['General']['startGenerationToken'] == mem_map.readline():
        try:
            other_socket = _socket.accept()
            sockets_queue.put(other_socket)
        except socket.timeout:
            pass
        mem_map.seek(0)

    _socket.close()
    with open(server_log_file, 'a') as _file:
        _file.write(str(time.time()) + ' Joining queue tasks.\n')
    sockets_queue.join()

    with open(server_log_file, 'a') as _file:
        _file.write(str(time.time()) + ' Exiting...\n')
    mem_map.close()


if __name__ == '__main__':
    main(sys.argv[1:])
