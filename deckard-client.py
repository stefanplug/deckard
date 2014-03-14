#!/usr/bin/python
import ConfigParser
import sys
import getopt
import argparse
import socket
import json

def usage():
    print("Usage: decard-client -s 127.0.0.1 -p 1337\n\n"
        "\t-s[erver] 127.0.0.1     *IP address\n"
        "\t-p[ort] 1337            *Port number\n"
        "\t-v                      *Verbose mode\n"
    )
    sys.exit(2)

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.sendall(message)
    sock.settimeout(5.0)
    msg = sock.recv(1024)
    msg_decoded = json.loads(msg)
    print(msg_decoded)
    for key, value in msg_decoded.iteritems():
        print key, value
    #if "ERROR" in response:
    #    print(response)
    #if "UPDATE" in response:
    #    print(response)
        #    parsed = json.loads(response)

def check_node(ip):


def main(argv):
    # first parameters, then config file, else print help output
    opts, args = getopt.getopt(argv, "s:p:hv", ['server=',
                                                'port=',
                                                'help',
                                                'verbose',
                                               ])
    if opts == []: 
        usage()

    # assign parameters to variables
    port = 1337
    verbose = 0
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-s", "--server"):
            ip = str(arg)
        elif opt in ("-p", "--port"):
            port = int(arg)
        elif opt in ("-v", "--verbose"):
            verbose = 1
    # start connecting
    client(ip, port, "hello")

if __name__ == "__main__":
    main(sys.argv[1:])
