#!/usr/bin/env python3
import fcntl
import struct
import os
import socket
import select
import ssl
import spwd
import crypt
from scapy.all import *

TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000

def connX(IP, PORT, context):
    # set up socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    sock.bind((IP, PORT))
    sock.listen(5)

    # wrap socket and accept connection
    tls_sock = context.wrap_socket(sock, server_side=True)
    conn, _ = tls_sock.accept()

    return conn

def client_auth(connection):
    # recieve username and check shadow file to see if user exists
    username = connection.recv(1024).decode()
    try:
        spwd.getspnam(username).sp_namp
    except KeyError:
        connection.send("False".encode())
        print("Client profile {} does not exist, closing connection".format(username))
        connection.close()
        exit(0)
    else:
        connection.send("True".encode())

    # recieve password from client
    password = connection.recv(1024).decode()

    #check shadow file for password of input username
    shadow = spwd.getspnam(username).sp_pwdp

    # encrypt input password
    crypt_password = crypt.crypt(password, shadow)

    # check if passwords are the same
    if crypt_password != shadow:
        connection.send("False".encode())
        print("Client entered incorrect password, closing connection")
        connection.close()
        return False
    else:
        connection.send("True".encode())
        connection.close()
        return True

# create the TUN interface and get its name
tun = os.open("/dev/net/tun", os.O_RDWR)
ifr = struct.pack('16sH', b'tun%d', IFF_TUN | IFF_NO_PI)
ifname_bytes = fcntl.ioctl(tun, TUNSETIFF, ifr)
ifname = ifname_bytes.decode('utf-8')[:16].strip('\x00')

# set up the interface
os.system("ip addr add 10.0.53.1/24 dev {}".format(ifname))
os.system("ip link set dev {} up".format(ifname))

# provide context for the ssl connection
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="./newservcert.pem", keyfile="./server-key.pem")

# set up connection to prompt for password
conn = connX('0.0.0.0', 9090, context)

# ask client for password, run program if correct
if client_auth(conn):
    # set up tunnel connection
    print("Created TUN interface: {}".format(ifname))
    conn = connX('0.0.0.0', 9091, context)
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
else:
    exit(0)