"""Utility functions."""

from ConfigParser import RawConfigParser
import logging

logger = logging.getLogger(__name__)


def get_dirs(fresh=False):
    """
    returns a dict that contains absolute paths to the project
    directories.
    If fresh=True, the dict is regenerated.
    """
    logger.debug("Called get_dirs with fresh=%s", fresh)
    if fresh == False and "dirs" in get_dirs.__dict__:
        logger.debug("get_dirs returned with result: %s", get_dirs.dirs)
        return get_dirs.dirs

    # TODO: See how to fix this?!
    home_path = '/home/sdm/SDN-Monitoring/'

    get_dirs.dirs = {
        'home': home_path,
        'config': home_path + 'config/',
        'util': home_path + 'util/',
        'src': home_path + 'src/SDM/',
        'log': home_path + 'logs/',
        'bin': home_path + 'bin/',
        'tmp': home_path + 'tmp/'
    }
    logger.debug("get_dirs returned with result: %s", get_dirs.dirs)
    return get_dirs.dirs


def get_params(directories, fresh=False):
    """
    returns a dict that contains the parameters specified
    in ${PROJ_PATH}\\config\\parameters.cfg.
    If fresh=True, the dist is regenerated.
    """
    logger.debug("Called get_params with fresh=%s", fresh)
    if fresh == False and "params" in get_params.__dict__:
        logger.debug("get_params returned with result: %s", get_params.params)
        return get_params.params

    config = RawConfigParser()
    config.read(directories['config'] + 'parameters.cfg')

    params = {'RunParameters': {}, 'General': {}, 'Client': {}, 'Server': {}, 'FlowLimits': {}}

    number_of_stations = config.getint('RunParameters', 'numberOfStations')
    params['RunParameters']['numberOfStations'] = number_of_stations
    params['RunParameters']['topoType'] = config.get('RunParameters',
                                                     'topoType')
    local_bandwidth = config.getfloat('RunParameters', 'localBw')
    params['RunParameters']['localBw'] = local_bandwidth
    params['RunParameters']['maxBw'] = local_bandwidth * number_of_stations
    params['RunParameters']['timeStep'] = config.getfloat('RunParameters',
                                                          'timeStep')
    params['RunParameters']['state'] = config.get('RunParameters',
                                                  'state')
    params['RunParameters']['ryuApps'] = config.get('RunParameters',
                                                    'ryuApps')

    params['General']['fileToSendPath'] = directories['home'] + \
                                          config.get('General', 'fileToSendPath')
    params['General']['sharedMemFilePath'] = directories['home'] + \
                                             config.get('General', 'sharedMemFilePath')
    params['General']['startGenerationToken'] = config.get('General',
                                                           'startGenerationToken')
    params['General']['finishGenerationToken'] = config.get('General',
                                                            'finishGenerationToken')
    params['General']['alertToken'] = config.get('General',
                                                            'alertToken')
    params['General']['recvSize'] = config.getint('General', 'recvSize')
    params['General']['ipBase'] = config.get('General', 'ipBase')
    params['General']['xterms'] = config.getboolean('General', 'xterms')
    params['General']['cleanup'] = config.getboolean('General', 'cleanup')
    params['General']['inNameSpace'] = config.getboolean('General',
                                                         'inNameSpace')
    params['General']['autoSetMacs'] = config.getboolean('General',
                                                         'autoSetMacs')
    params['General']['autoStaticArp'] = config.getboolean('General',
                                                           'autoStaticArp')
    params['General']['autoPinCpus'] = config.getboolean('General',
                                                         'autoPinCpus')
    params['General']['controllerIP'] = config.get('General', 'controllerIP')
    params['General']['controllerPort'] = config.getint('General',
                                                        'controllerPort')
    params['General']['listenPort'] = config.getint('General', 'listenPort')

    params['Client']['numberOfThreads'] = config.getint('Client',
                                                        'numberOfThreads')
    params['Client']['maxConnections'] = config.getint('Client',
                                                       'maxConnections')
    params['Client']['maxSleepDelay'] = config.getfloat('Client',
                                                        'maxSleepDelay')

    params['Server']['drainTimeout'] = config.getfloat('Server',
                                                       'drainTimeout')
    params['Server']['numberOfThreads'] = config.getint('Server',
                                                        'numberOfThreads')
    params['Server']['port'] = config.getint('Server', 'port')

    for (name, value) in config.items('FlowLimits'):
        params['FlowLimits'][name] = float(value)

    get_params.params = params
    logger.debug("get_params returned with result: %s", get_params.params)
    return get_params.params


def irange(start, end):
    """
    Inclusive range from start to end (vs. Python insanity.)
    irange(1,5) -> 1, 2, 3, 4, 5
    Credit: Mininet's util library.
    """
    return range(start, end + 1)


def ipv4_to_int(s):
    """
    Convert dotted IPv4 address to integer.
    Credit: https://gist.github.com/cslarsen/1595135
    """
    return reduce(lambda a, b: a << 8 | b, map(int, s.split(".")))


def int_to_ipv4(ip):
    """
    Convert 32-bit integer to dotted IPv4 address.
    Credit: https://gist.github.com/cslarsen/1595135
    """
    return ".".join(map(lambda n: str(ip >> n & 0xFF), [24, 16, 8, 0]))


# noinspection PyPep8Naming
def CIDR_mask_to_ipv4_subnet_mask(CIDR_mask):
    assert 0 <= CIDR_mask <= 32
    res = ''
    full_levels = CIDR_mask / 8
    curr_level = CIDR_mask % 8
    empty_levels = 4 - 1 - CIDR_mask / 8
    for i in range(0, full_levels):
        res += '255.'
    if full_levels < 4:
        curr_level_mask = 0
        for i in range(0, curr_level):
            curr_level_mask = (curr_level_mask << 1) | 1
        for i in range(curr_level, 8):
            curr_level_mask = (curr_level_mask << 1) | 0
        res = res + str(curr_level_mask) + '.'
    for i in range(0, empty_levels):
        res += '0.'
    return res[:-1]


def get_index_of_least_sig_one(ipv4_string):
    ip_arr = ipv4_string.split(".")[::-1]
    assert len(ip_arr) == 4
    res = 32
    curr = ''
    for ip in ip_arr:
        if int(ip) == 0:
            res -= 8
        else:
            curr = bin(int(ip))[2:].zfill(8)[::-1]
            break
    if res == 0:
        return res
    for i in range(0, 8):
        if int(curr[i]) == 0:
            res -= 1
        else:
            break
    return res


def get_paired_ipv4(ipv4_string, mask_ip):
    assert len(ipv4_string.split(".")) == 4
    assert len(mask_ip.split(".")) == 4
    ls1 = get_index_of_least_sig_one(mask_ip)
    tmp = "1".zfill(ls1)[::-1]
    xor_mask = int("0b" + tmp.zfill(32)[::-1], 2)
    ip_int = ipv4_to_int(ipv4_string)
    ip_int ^= xor_mask
    return int_to_ipv4(ip_int)


def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m
