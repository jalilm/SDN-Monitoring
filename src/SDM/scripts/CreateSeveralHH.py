import random
import os
import sys
import glob

attack_packet_size = 74
attack_bw = 20
nomral_packet_size = 54
normal_bw = 7

ips = ["232.228.72.51", "101.126.226.63", "158.69.233.242", "37.14.81.34", "144.224.121.58", "83.179.5.40",
       "68.142.4.60", "201.127.187.201", "101.3.102.228", "232.196.174.105"]

def get_ips(num, common_mask, ipv4_to_int, int_to_ipv4):
    random.shuffle(ips)
    if common_mask == 0: # choose randomly from ips list.
        assert len(ips) >= num
        return ips[0:num]
    else:
        assert pow(2,32-common_mask) >= num
        ip_int = ipv4_to_int(ips[0])
        for k in range(0,32-common_mask):
            ip_int = (ip_int & ~(1 << k)) | (0 << k)
        j = 0
        while j < num:
                suffix_ip = random.randint(0,pow(2,32-common_mask)-1)
                new_ip = int_to_ipv4(ip_int + suffix_ip)
                if new_ip not in ips[0:j]:
                        try:
                                ips[j] = new_ip
                        except IndexError:
                                ips.append(new_ip)
                        j += 1
        return ips[0:num]

def create_packet(ip):
    command = "tcprewrite -C -S 0.0.0.0/0:" + ip + "/32 --infile=/home/sdm/SDN-Monitoring/tmp/tcp.pcap --outfile=/home/sdm/SDN-Monitoring/tmp/tcp-" + ip + ".pcap"
    os.system(command)

def combine_packets(num, ips):
    for ip in ips:
        if not os.path.isfile("/home/sdm/SDN-Monitoring/tmp/tcp-" + ip + ".pcap"):
            create_packet(ip)

    if os.path.isfile("/home/sdm/SDN-Monitoring/tmp/several.pcap"):
        os.system("rm /home/sdm/SDN-Monitoring/tmp/several.pcap")

    os.system("cp /home/sdm/SDN-Monitoring/tmp/tcp-" + ips[0] + ".pcap /home/sdm/SDN-Monitoring/tmp/several.pcap")

    for ip in ips[1:]:
        os.system("mergecap -a -w /home/sdm/SDN-Monitoring/tmp/x.pcap /home/sdm/SDN-Monitoring/tmp/several.pcap /home/sdm/SDN-Monitoring/tmp/tcp-" + ip + ".pcap")
        os.system("mv /home/sdm/SDN-Monitoring/tmp/x.pcap /home/sdm/SDN-Monitoring/tmp/several.pcap")

    os.system("rm /home/sdm/SDN-Monitoring/tmp/tcp-*.pcap")
    os.system("cp /home/sdm/SDN-Monitoring/tmp/several.pcap /home/sdm/SDN-Monitoring/tmp/x.pcap")

    for i in range(1, 540/num):
	os.system("mergecap -a -w /home/sdm/SDN-Monitoring/tmp/y.pcap /home/sdm/SDN-Monitoring/tmp/several.pcap /home/sdm/SDN-Monitoring/tmp/x.pcap")
        os.system("mv /home/sdm/SDN-Monitoring/tmp/y.pcap /home/sdm/SDN-Monitoring/tmp/several.pcap")

    os.system("rm /home/sdm/SDN-Monitoring/tmp/x.pcap")
	
    for f in glob.glob('/home/sdm/CAIDA-DLT/tmp/split_00000*'):
	os.system("mergecap -a -w /home/sdm/SDN-Monitoring/tmp/y.pcap /home/sdm/SDN-Monitoring/tmp/several.pcap" + " " +str(f))
	os.system("mv /home/sdm/SDN-Monitoring/tmp/y.pcap /home/sdm/SDN-Monitoring/tmp/several.pcap")

    os.system("editcap -S0 /home/sdm/SDN-Monitoring/tmp/several.pcap /home/sdm/SDN-Monitoring/tmp/y.pcap")
    os.system("mv /home/sdm/SDN-Monitoring/tmp/y.pcap /home/sdm/SDN-Monitoring/tmp/several.pcap")

def create(num, common_mask, ipv4_to_int, int_to_ipv4):
    combine_packets(num, get_ips(num, common_mask, ipv4_to_int, int_to_ipv4))
