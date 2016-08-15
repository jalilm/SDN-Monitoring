#!/usr/bin/env python

import glob
import os

import matplotlib.pyplot as plt


def main():
    res_per_k = {}
    for fn in glob.glob(os.path.expanduser('~/logs/') + '*-Topk-*'):
        if os.path.isfile(fn):
            #bfn = os.path.basename(fn)
            #mechanism, topk, rate, directory, timestep, hh, cm = bfn.split('-')
            with open(fn, "r") as f:
                f_res = f.readlines()
                for l in f_res:
                    found = int(l.split(':')[1])
                    k = int(l.split(':')[0].split(' ')[0])
                    counters = int(l.split(':')[0].split(' ')[1])
                    try:
                        res_per_k[k][counters] = found
                    except KeyError:
                        res_per_k[k] = {counters: found}

    for k in res_per_k.keys():
        res = []
        counters = []
        sorted_res_per_k = sorted(res_per_k[k], key=lambda x: x)
        for counter in sorted_res_per_k:
            counters.append(counter)
            res.append(100.0 * (res_per_k[k][counter]) / k)
        plt.plot(counters, res, marker=(4, k % 4, 360 / k), label='k=' + str(k))
        plt.ylim((0, 100))
        plt.ylabel('percentage')
        plt.xlabel('counters')
        plt.title('Percentage of found top-k flows')
        plt.legend(numpoints=1)
    plt.show()


if __name__ == '__main__':
    main()
