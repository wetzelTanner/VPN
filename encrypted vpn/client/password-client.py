#!/usr/bin/env python3
import fcntl
import struct
import os
import socket
import select
import ssl
import time
import getpass
from scapy.all import *

TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000

def connX(IP, PORT, hostname):
    # set up socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((IP, PORT))

    # wrap socket
    ssock = context.wrap_socket(sock, server_hostname=hostname)
    
    return ssock

def give_pass(socket):
    # send input username to server
    username = input("Enter your username: ")
    socket.send(username.encode())

    # handle response from server
    if socket.recv(1024).decode() == 'True':
        # send password to server
        password = getpass.getpass("Enter your password: ", stream=None)
        socket.send(password.encode())
    else:
        print("User {} does not exist, closing connection".format(username))
        socket.close()
        exit(0)

    # recieve password auth reply
    if socket.recv(1024).decode() == 'True':
        print("Establishing connection...")
    else:
        print("Incorrect password for {}. Closing connection.".format(username))
        socket.close()
        exit(0)
    socket.close()

# create the TUN interface and get its name
tun = os.open("/dev/net/tun", os.O_RDWR)
ifr = struct.pack('16sH', b'tun%d', IFF_TUN | IFF_NO_PI)
ifname_bytes = fcntl.ioctl(tun, TUNSETIFF, ifr)
ifname = ifname_bytes.decode('utf-8')[:16].strip('\x00')

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

# create TCP socket to give password to server
tls_sock = connX('10.0.2.8', 9090, hostname)

# give username and password to server
give_pass(tls_sock)
time.sleep(1)

# create TCP socket for TUN interface
print("Created TUN interface: {}".format(ifname))
tls_sock = connX('10.0.2.8', 9091, hostname)
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