#!/usr/bin/python
import ConfigParser
import socket
import threading

config = ConfigParser.ConfigParser()
config.read("client.cfg")
ip = config.get("Client", "ip")
port = config.getint("Client", "port")

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print("Received: {}".format(response))
    finally:
        sock.close()

if __name__ == "__main__":
    client(ip, port, "Hello")
