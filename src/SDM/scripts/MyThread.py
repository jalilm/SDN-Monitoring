"""
An abstract subclass that represents a thread
deriving from threading.Thread and supplies
extra functionality.
"""

from threading import Thread
import time


class MyThread(Thread):
    """
    An abstract subclass that represents a thread
    deriving from threading.Thread and supplies
    extra functionality.
    """

    def __init__(self, thread_id, name, kind, logs_dir_path):
        super(MyThread, self).__init__()
        self.thread_id = thread_id
        self.name = name
        self.kind = kind
        self.thread_file = logs_dir_path + self.kind + '_' + \
                           str(self.thread_id) + '_' + str(self.name) + '_log'
        self.log('started')

    def log(self, msg):
        """
        writes msg to the thread's file.
        """
        with open(self.thread_file, 'a') as log_file:
            log_file.write(str(time.time()) + ' ' + str(self.name) + \
                           ': ' + str(msg) + '\n')
