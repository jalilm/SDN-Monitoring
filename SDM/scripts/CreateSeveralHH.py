import glob
import os
import random

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

def create_packet(dirs, ip):
    command = "tcprewrite -C -S 0.0.0.0/0:" + ip + "/32 --infile=" + dirs['tmp'] + "tcp.pcap --outfile=" + dirs['tmp'] + "tcp-" + ip + ".pcap"
    os.system(command)

def combine_packets(dirs, num, ips):
    for ip in ips:
        if not os.path.isfile(dirs['tmp']+"tcp-" + ip + ".pcap"):
            create_packet(dirs, ip)

    if os.path.isfile(dirs['tmp'] + "several.pcap"):
        os.system("rm" + dirs['tmp'] + "several.pcap")

    os.system("cp " + dirs['tmp'] + "tcp-" + ips[0] + ".pcap " + dirs['tmp'] + "several.pcap")

    for ip in ips[1:]:
        os.system("mergecap -a -w " + dirs['tmp'] + "x.pcap " + dirs['tmp'] + "several.pcap " + dirs['tmp'] + "tcp-" + ip + ".pcap")
        os.system("mv " + dirs['tmp'] + "x.pcap " + dirs['tmp'] + "several.pcap")

    os.system("rm " + dirs['tmp'] + "tcp-*.pcap")
    os.system("cp " + dirs['tmp'] + "several.pcap " + dirs['tmp'] + "x.pcap")

    for i in range(1, 540/num):
	os.system("mergecap -a -w " + dirs['tmp'] + "y.pcap " + dirs['tmp'] + "several.pcap " + dirs['tmp'] + "x.pcap")
        os.system("mv " + dirs['tmp'] + "y.pcap " + dirs['tmp'] + "several.pcap")

    os.system("rm " + dirs['tmp'] + "x.pcap")
	
    for f in glob.glob('~/CAIDA-DLT/tmp/split_00000*'):
	os.system("mergecap -a -w " + dirs['tmp'] + "y.pcap " + dirs['tmp'] + "several.pcap" + " " +str(f))
	os.system("mv " + dirs['tmp'] + "y.pcap " + dirs['tmp'] + "several.pcap")

    os.system("editcap -S0 " + dirs['tmp'] + "several.pcap " + dirs['tmp'] + "y.pcap")
    os.system("mv " + dirs['tmp'] + "y.pcap " + dirs['tmp'] + "several.pcap")

def create(dirs, num, common_mask, ipv4_to_int, int_to_ipv4):
    combine_packets(dirs, num, get_ips(num, common_mask, ipv4_to_int, int_to_ipv4))