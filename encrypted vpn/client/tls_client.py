#!/usr/bin/env python3
import fcntl
import struct
import os
import socket
import select
import ssl
from scapy.all import *

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
os.system("ip addr add 10.0.53.99/24 dev {}".format(ifname))
os.system("ip link set dev {} up".format(ifname))
os.system("ip route add 192.168.56.0/24 dev {}".format(ifname))

# provide server hostname and ssl client context
hostname = "tanner-aj-vpn.com"
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations(cafile="./newservcert.pem")
context.verify_mode = ssl.CERT_REQUIRED
context.check_hostname = True

# create TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('10.0.2.8', 9090))

# Wrap the socket with SSL
tls_sock = context.wrap_socket(sock, server_hostname=hostname)

fds = [tls_sock, tun]

while True:
    ready, _, _ = select.select(fds, [], [])

    for fd in ready:
        if fd is tls_sock:
            data = tls_sock.recv(2048)  # retrieve the packet
            pkt = IP(data)
            print("From socket <==: {} --> {}".format(pkt.src, pkt.dst))
            os.write(tun, data)  # give the packet to the kernel

        if fd is tun:
            packet = os.read(tun, 2048)
            pkt = IP(packet)
            print("From tun      ==>: {} --> {}".format(pkt.src, pkt.dst))
            tls_sock.sendall(packet)