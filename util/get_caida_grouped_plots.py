#!/usr/bin/env python

import os

import matplotlib.pyplot as plt
import numpy as np


def main():
    k = 20
    for i in range(0, 60):
        second = "%02d" % i
        os.system("cd " + os.path.expanduser('~/CAIDA-DLT/') + "sec" + second + "/")
        diff = []
        cidr_strings = []
        for c in range(0, 33):
            cidr = "%02d" % c
            cidr_strings.append("/" + str(c))
            os.system("cat ./sec" + second + "-groupedBy-" + cidr + "CIDR.stat" \
                      + " | cut -d\" \" -f2 > ./tmp" + second + "s" + cidr + "c")
            with open("./tmp" + second + "s" + cidr + "c", 'r') as f:
                bps = f.readlines()[:k]
                diff.append((int(bps[0]) - int(bps[-1:][0])) / len(bps))
            os.system("rm ./tmp" + second + "s" + cidr + "c")

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
        xtick_names = ax.set_xticklabels(cidr_strings)
        plt.setp(xtick_names, fontsize=8)
        fig.savefig("sec" + second + "-averageDiff.jpg", dpi=100)
        plt.close()
        os.system("cd ..")


if __name__ == '__main__':
    main()
