#!/usr/bin/python
import ConfigParser
import sys
import getopt
import socket
import json
import logging

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
    try:
        msg = sock.recv(1024)
    except socket.timeout:
        logging.error("Connection to server timed out")
        quit()
    msg_decoded = json.loads(msg)
    logging.info(msg_decoded)
    for key, value in msg_decoded.iteritems():
        logging.info(key, value)
        if key == "UPDATE":
            for slave in value:
                check_node(slave)
        if key == "ERROR":
            logging.error("Maybe you are already known.")
    #if "ERROR" in response:
    #    print(response)
    #if "UPDATE" in response:
    #    print(response)
        #    parsed = json.loads(response)

#def check_node(ip):


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
    #log = logging
    #log.basicConfig(format="%(levelname)s: %(message)s")
    # create logger
    log = logging
    loglevel = log.WARNING
    port = 1337
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-s", "--server"):
            ip = str(arg)
        elif opt in ("-p", "--port"):
            port = int(arg)
        elif opt in ("-v", "--verbose"):
            loglevel=log.DEBUG
    # start connecting
    log.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=loglevel)
    client(ip, port, "hello")

if __name__ == "__main__":
    main(sys.argv[1:])
