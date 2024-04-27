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
os.system("ip addr add 10.0.53.1/24 dev {}".format(ifname))
os.system("ip link set dev {} up".format(ifname))

# provide context for the ssl connection
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="./newservcert.pem", keyfile="./server-key.pem")

# set up the socket
IP_A = "0.0.0.0"
PORT = 9090
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.bind((IP_A, PORT))
sock.listen(5)  # listen for incoming connections

# wrap the socket with SSL
tls_sock = context.wrap_socket(sock, server_side=True)
conn, _ = tls_sock.accept()

fds = [tun, conn]

while True:
    ready, _, _ = select.select(fds, [], [])

    for fd in ready:
        if fd is conn:
            # send to the TUN interface
            packet = conn.recv(2048)
            pkt = IP(packet)
            print("From socket <==: {} --> {}".format(pkt.src, pkt.dst))
            os.write(tun, packet)

        if fd is tun:
            # send to connected client
            packet = os.read(tun, 2048)
            pkt = IP(packet)
            print("From tun      ==>: {} --> {}".format(pkt.src, pkt.dst))
            conn.send(packet)