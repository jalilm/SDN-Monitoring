"""Utility functions."""

import math
import os
from ConfigParser import RawConfigParser

from src.SDM.scripts.CreateSeveralHH import create


def ipv4_partition(k):
    """
    partitions the ipv4 address space into k disjoint partitions.
    :param k: the number of partitions.
    :return: a dictionary contains strings of the partitions.
    """
    assert math.log(k,2)%1 == 0
    ips = []
    for j in range(0, k):
        ip_int = j*pow(2,32-int(math.log(k,2)))
        ips.append(int_to_ipv4(ip_int))
    return ips


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

def get_dirs(fresh=False):
    """
    returns a dict that contains absolute paths to the project
    directories.
    If fresh=True, the dict is regenerated.
    """
    if fresh == False and "dirs" in get_dirs.__dict__:
        return get_dirs.dirs

    home_path = os.path.expanduser('~/')

    get_dirs.dirs = {
        'home': home_path,
        'config': home_path + 'config/',
        'util': home_path + 'util/',
        'src': home_path + 'src/SDM/',
        'log': home_path + 'logs/',
        'bin': home_path + 'bin/',
        'tmp': home_path + 'tmp/'
    }
    return get_dirs.dirs


def get_params(directories, fresh=False):
    """
    returns a dict that contains the parameters specified
    in ${PROJ_PATH}\\config\\parameters.cfg.
    If fresh=True, the dist is regenerated.
    """
    if fresh == False and "params" in get_params.__dict__:
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
    state = config.get('RunParameters', 'state')
    params['RunParameters']['state'] = state
    rate_type = config.get('RunParameters', 'rate_type')
    params['RunParameters']['rate_type'] = rate_type
    direction = config.get('RunParameters', 'direction')
    params['RunParameters']['direction'] = direction
    params['RunParameters']['interact'] = config.getboolean('RunParameters', 'interact')
    params['RunParameters']['numHH'] = 1
    params['RunParameters']['mechanism'] = config.get('RunParameters',
                                                     'mechanism')
    params['RunParameters']['common_mask'] = config.getint('RunParameters', 'common_mask')
    params['RunParameters']['before_attack'] = directories['home'] + "util/before_trace"
    params['RunParameters']['after_attack'] = directories['home'] + "util/after_trace"

    if state == "Pulling":
        params['RunParameters']['test'] = "src.SDM.tests.TraceTest.TraceTest"
        params['RunParameters']['numberOfStations'] = 2
        if rate_type == "BW":
            params['RunParameters']['topoType'] = "src.SDM.topologies.TraceTopo.TraceTopo"
            params['RunParameters']['attack'] = directories['home'] + "util/bw-attack"
            if direction == "Destination":
                params['RunParameters']['ryuApps'] = directories['home'] + "src/SDM/apps/BWPullingController.py"
                params['RunParameters']['Datapath'] = "src.SDM.nodes.BWPullingDatapath.BWPullingDatapath"
            if direction == "Source":
                params['RunParameters']['ryuApps'] = directories['home'] + "src/SDM/apps/SrcBWPullingController.py"
                params['RunParameters']['Datapath'] = "src.SDM.nodes.SrcBWPullingDatapath.SrcBWPullingDatapath"
        if rate_type == "Syn":
            params['RunParameters']['topoType'] = "src.SDM.topologies.SynTraceTopo.SynTraceTopo"
            params['RunParameters']['attack'] = directories['home'] + "util/syn-attack"
            if direction == "Destination":
                params['RunParameters']['ryuApps'] = directories['home'] + "src/SDM/apps/SynPullingController.py"
                params['RunParameters']['Datapath'] = "src.SDM.nodes.SynPullingDatapath.SynPullingDatapath"
            if direction == "Source":
                params['RunParameters']['ryuApps'] = directories['home'] + "src/SDM/apps/SrcSynPullingController.py"
                params['RunParameters']['Datapath'] = "src.SDM.nodes.SrcSynPullingDatapath.SrcSynPullingDatapath"
        if rate_type == "HH-several":
            assert False

    if state == "Topk":
        params['RunParameters']['test'] = "src.SDM.tests.DoubleKTest.DoubleKTest"
        params['RunParameters']['numberOfStations'] = 2
        params['RunParameters']['k'] = config.getint('RunParameters', 'k')
        params['RunParameters']['counters'] = config.getint('RunParameters', 'counters')
        params['RunParameters']['topoType'] = "src.SDM.topologies.TraceTopo.TraceTopo"
        params['RunParameters']['before_attack'] = ''
        params['RunParameters']['attack'] = directories['home'] + "util/topk_trace"
        params['RunParameters']['after_attack'] = ''
        if direction == "Destination":
            assert False
        if direction == "Source":
            params['RunParameters']['ryuApps'] = directories['home'] + "src/SDM/apps/SrcBWTopkController.py"
            params['RunParameters']['Datapath'] = "src.SDM.nodes.SrcBWTopkDatapath.SrcBWTopkDatapath"
        if rate_type == "BW":
            params['RunParameters']['tempStepChange'] = "normal"
        elif rate_type == "IncreasingBW":
            params['RunParameters']['tempStepChange'] = "positive"
        elif rate_type == "DecreasingBW":
            params['RunParameters']['tempStepChange'] = "negative"
        elif rate_type == "IncDecBW":
            params['RunParameters']['tempStepChange'] = "posneg"
        if rate_type == "Syn":
            assert False
        if rate_type == "HH-several":
            assert False

    if state == "Pushing":
        params['RunParameters']['test'] = "src.SDM.tests.TraceTest.TraceTest"
        params['RunParameters']['numberOfStations'] = 2
        params['RunParameters']['mininet_switch'] = "src.SDM.nodes.PushingSwitch.PushingSwitch"
        if rate_type == "BW":
            params['RunParameters']['topoType'] = "src.SDM.topologies.TraceTopo.TraceTopo"
            params['RunParameters']['ryuApps'] = directories['home'] + "src/SDM/apps/PushingController.py"
            params['RunParameters']['attack'] = directories['home'] + "util/bw-attack"
            if direction == "Destination":
                params['RunParameters']['Datapath'] = "src.SDM.nodes.BWPushingDatapath.BWPushingDatapath"
                params['RunParameters']['middleware'] = "src.SDM.nodes.BWMiddleWare.BWMiddleWare"
            if direction == "Source":
                params['RunParameters']['Datapath'] = "src.SDM.nodes.SrcBWPushingDatapath.SrcBWPushingDatapath"
                params['RunParameters']['middleware'] = "src.SDM.nodes.SrcBWMiddleWare.SrcBWMiddleWare"
        if rate_type == "Syn":
            params['RunParameters']['topoType'] = "src.SDM.topologies.SynTraceTopo.SynTraceTopo"
            params['RunParameters']['ryuApps'] = directories['home'] + "src/SDM/apps/Pushing15Controller.py"
            params['RunParameters']['attack'] = directories['home'] + "util/syn-attack"
            if direction == "Destination":
                params['RunParameters']['Datapath'] = "src.SDM.nodes.SynPushingDatapath.SynPushingDatapath"
                params['RunParameters']['middleware'] = "src.SDM.nodes.SynMiddleWare.SynMiddleWare"
            if direction == "Source":
                params['RunParameters']['Datapath'] = "src.SDM.nodes.SrcSynPushingDatapath.SrcSynPushingDatapath"
                params['RunParameters']['middleware'] = "src.SDM.nodes.SrcSynMiddleWare.SrcSynMiddleWare"
        if rate_type == "HH-several":
            if direction == "Destination":
                assert False
            f1 = ipv4_to_int
            f2 = int_to_ipv4
            params['RunParameters']['numHH'] = config.getint('RunParameters', 'numHH')
            create(get_dirs(), params['RunParameters']['numHH'], params['RunParameters']['common_mask'], f1, f2)
            params['RunParameters']['topoType'] = "src.SDM.topologies.TraceTopo.TraceTopo"
            params['RunParameters']['ryuApps'] = directories['home'] + "src/SDM/apps/PushingController.py"
            params['RunParameters']['attack'] = directories['home'] + "util/several-attack"
            params['RunParameters']['Datapath'] = "src.SDM.nodes.SrcBWPushingDatapath.SrcBWPushingDatapath"
            params['RunParameters']['middleware'] = "src.SDM.nodes.SrcBWMiddleWare.SrcBWMiddleWare"

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
    return get_params.params


def irange(start, end):
    """
    Inclusive range from start to end (vs. Python insanity.)
    irange(1,5) -> 1, 2, 3, 4, 5
    Credit: Mininet's util library.
    """
    return range(start, end + 1)

def bytes_to_ipv4(ip):
    int_ip = sum(ord(c) << (i * 8) for i, c in enumerate(ip[::-1]))
    return int_to_ipv4(int_ip)


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
