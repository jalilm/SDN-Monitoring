__author__ = 'jalilm'

import logging

from SDM.util import get_dirs

log_file = get_dirs()['log'] + 'SDM.log'
logging.basicConfig(filename=log_file, filemode='w', level=logging.INFO,
                    format='%(created)f %(module)s:%(levelname)s %(message)s')
