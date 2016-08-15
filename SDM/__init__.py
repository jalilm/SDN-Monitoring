import logging
import util

log_file = util.get_dirs()['log'] + 'SDM.log'
logging.basicConfig(filename=log_file, filemode='w', level=logging.INFO,
                    format='%(created)f %(module)s:%(levelname)s %(message)s')
