#!/usr/bin/env python

import os
import sys

import matplotlib.pyplot as plt
import numpy as np


def main(argv):
    k = 20
    for i in range(0, 60):
        second = "%02d" % i
        os.system("cd " + os.path.expanduser('~/CAIDA-DLT/') + "sec" + second + "/")
        diff = []
        CIDRStrings = []
        for c in range(0, 33):
            CIDR = "%02d" % c
            CIDRStrings.append("/" + str(c))
            os.system("cat ./sec" + second + "-groupedBy-" + CIDR + "CIDR.stat" \
                      + " | cut -d\" \" -f2 > ./tmp" + second + "s" + CIDR + "c")
            with open("./tmp" + second + "s" + CIDR + "c", 'r') as f:
                bps = f.readlines()[:k]
                diff.append((int(bps[0]) - int(bps[-1:][0])) / len(bps))
            os.system("rm ./tmp" + second + "s" + CIDR + "c")

        fig = plt.figure()
        ind = np.arange(33)  # the x locations for the groups
        width = 0.1  # the width of the bars
        ax = fig.add_subplot(111)
        ax.bar(ind, diff, width)
        ax.set_xlim(-width, len(ind) + width)
        ax.set_ylabel('BW')
        ax.set_xlabel('CIDR')
        ax.set_title('average diff from top-1 to top-' + str(k))
        ax.set_xticks(ind + width)
        xtickNames = ax.set_xticklabels(CIDRStrings)
        plt.setp(xtickNames, fontsize=8)
        fig.savefig("sec" + second + "-averageDiff.jpg", dpi=100)
        plt.close()
        os.system("cd ..")


if __name__ == '__main__':
    main(sys.argv)
