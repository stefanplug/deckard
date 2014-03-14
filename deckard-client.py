#!/usr/bin/python
import ConfigParser
import socket
import threading
import re
import pickle
import json

config = ConfigParser.ConfigParser()
config.read("client.cfg")
ip = config.get("Client", "ip")
port = config.getint("Client", "port")

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        sock.settimeout(5.0)
        response = sock.recv(1024)
        if "ERROR" in response:
            print(response)
        if "UPDATE" in response:
            print(response)
            parsed = json.loads(response)
            print(parsed)
#        for b in response:
#            print(b)
        #print("Received: {}".format(response))
        
    finally:
        sock.close()

if __name__ == "__main__":
    client(ip, port, "hello")
