import random
import os
import sys

ips = ["232.228.72.51", "101.126.226.63", "158.69.233.242", "37.14.81.34", "144.224.121.58", "83.179.5.40",
       "68.142.4.60", "201.127.187.201", "101.3.102.228", "232.196.174.105"]


def get_ips(num):
    assert num <= 10
    assert num >= 1
    random.shuffle(ips)
    return ips[1:num + 1]


def create_packet(ip):
    command = "tcprewrite -C -S 0.0.0.0/0:" + ip + "/32 --infile=/home/sdm/SDN-Monitoring/tmp/tcp.pcap --outfile=/home/sdm/SDN-Monitoring/tmp/tcp-" + ip + ".pcap"
    os.system(command)

def combine_packets(ips):
    for ip in ips:
        if not os.path.isfile("/home/sdm/SDN-Monitoring/tmp/tcp-" + ip + ".pcap"):
            create_packet(ip)

    if os.path.isfile("/home/sdm/SDN-Monitoring/tmp/several.pcap"):
        os.system("rm /home/sdm/SDN-Monitoring/tmp/several.pcap")

    os.system("cp /home/sdm/SDN-Monitoring/tmp/tcp-" + ips[0] + ".pcap /home/sdm/SDN-Monitoring/tmp/several.pcap")

    for ip in ips[1:]:
        os.system("mergecap -a -w /home/sdm/SDN-Monitoring/tmp/x.pcap /home/sdm/SDN-Monitoring/tmp/several.pcap /home/sdm/SDN-Monitoring/tmp/tcp-" + ip + ".pcap")
        os.system("mv /home/sdm/SDN-Monitoring/tmp/x.pcap /home/sdm/SDN-Monitoring/tmp/several.pcap")

def create(num):
    combine_packets(get_ips(num))

if __name__ == "__main__":
    create(int(sys.argv[1]))
