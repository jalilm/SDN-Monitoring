__author__ = 'jalilm'

import logging
from util import get_dirs

log_file = get_dirs()['log'] + '/SDM.log'
logging.basicConfig(filename=log_file, filemode='w', level=logging.INFO)