import random

from mininet.topo import Topo

from SDM.util import irange


class ConnectedTopology(Topo):
    """
    A random generated topology, where all switches are connected.
    No self loops, or 2-cycles are allowed.
    """

    def __init__(self, k=1):
        super(ConnectedTopology, self).__init__()
        random_generator = random.Random()
        random_generator.seed()
        switches = []
        links = []
        for i in irange(1, k):
            switches.append(self.addSwitch('s%s' % i))
            self.addLink(switches[i - 1], self.addHost('h%s' % i))
            links.append(i - 1)
            links[i - 1] = [i - 1]
        random.shuffle(switches)
        num_links = random_generator.randint(k - 1, (k * (k - 1)) / 2)
        for i in irange(1, k - 1):
            prev_sw_idx = random_generator.randint(0, i - 1)
            self.addLink(switches[prev_sw_idx], switches[i])
            links[i].append(prev_sw_idx)
            links[prev_sw_idx].append(i)
            num_links -= 1
        available_switches = irange(0, k - 1)
        while num_links > 0:
            first_idx = random_generator.choice(available_switches)
            possible_links = filter(lambda x: x not in links[first_idx], irange(0, k - 1))
            if len(possible_links) == 0:
                available_switches.remove(first_idx)
                continue
            second_idx = random_generator.choice(possible_links)
            self.addLink(switches[first_idx], switches[second_idx])
            links[first_idx].append(second_idx)
            links[second_idx].append(first_idx)
            num_links -= 1
