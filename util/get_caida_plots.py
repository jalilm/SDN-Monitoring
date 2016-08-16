#!/usr/bin/env python

import os

import matplotlib.pyplot as plt


def main():
    for i in range(0, 60):
        second = "%02d" % i
        os.system("cd " + os.path.expanduser('~/CAIDA-DLT/') + "sec" + second + "/")
        os.system("cat ./sec" + second + ".stat | cut -d\" \" -f2 > ./tmp" + second)
        with open('./tmp' + second, 'r') as f:
            bps = f.readlines()
        plt.plot(range(1, 101), bps[:100])
        plt.ylabel('byte per second')
        plt.title('the ' + second + ' second')
        fig = plt.gcf()
        fig.savefig("./sec" + second + "stat.jpg", dpi=100)
        plt.close()
        os.system("cd ..")

    for i in range(0, 60):
        second = "%02d" % i
        os.system("cd " + os.path.expanduser('~/CAIDA-DLT/') + "sec" + second + "/")
        with open('./tmp' + second, 'r') as f:
            bps = f.readlines()
        plt.plot(range(1, 101), bps[:100])
        os.system('rm ' + './tmp' + second)
        os.system("cd ..")

    plt.ylabel('byte per second')
    plt.title('the first minute')
    fig = plt.gcf()
    fig.savefig("min00stat.jpg", dpi=100)
    plt.close()


if __name__ == '__main__':
    main()
