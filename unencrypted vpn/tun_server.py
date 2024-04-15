#!/usr/bin/env python3
import fcntl
import struct
import os
import socket
import select
from scapy.all import*

TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001  # this flag will be used
IFF_TAP = 0x0002
IFF_NO_PI = 0x1000

# create the TUN interface
tun = os.open("/dev/net/tun", os.O_RDWR)
ifr = struct.pack('16sH', b'tun%d', IFF_TUN | IFF_NO_PI)
ifname_bytes = fcntl.ioctl(tun, TUNSETIFF, ifr)

# Get the interface name
ifname = ifname_bytes.decode('utf-8')[:16].strip('\x00')
print("Created TUN interface: {}".format(ifname))

# set up the interface
os.system("ip addr add 10.0.53.1/24 dev {}".format(ifname))
os.system("ip link set dev {} up".format(ifname))

# set up the socket
IP_A = "0.0.0.0"
PORT = 9090
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP_A, PORT))

# initialize IP and port numbers (initial values do not matter)
ip = "0.0.0.0"
port = 10000

fds = [sock, tun]

while True:
    ready, _, _ = select.select(fds, [], [])

    for fd in ready:
        if fd is sock:
            data, (ip, port) = sock.recvfrom(2048) # retrieve the packet
            pkt = IP(data)
            print("From socket <==: {} --> {}".format(pkt.src, pkt.dst))
            os.write(tun, data) # give the packet to the kernel

        if fd is tun:
            packet = os.read(tun, 2048)
            pkt = IP(packet)
            print("From tun      ==>: {} --> {}".format(pkt.src, pkt.dst))
            sock.sendto(packet, (ip, port))