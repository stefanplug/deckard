#!/usr/bin/python3
#import ConfigParser
import sys
import getopt
import socket
import subprocess
import json
import logging

def usage():
    print("Usage: decard-client -s 127.0.0.1 -p 1337\n\n"
        "\t-s[erver] 127.0.0.1     *IP address\n"
        "\t-p[ort] 1337            *Port number\n"
        "\t-v                      *Verbose mode\n"
    )
    sys.exit(2)

def parse_slaves(dct):
    if 'UPDATE' in dct:
        return(dct['SLAVES'])

def parse_ttl(dct):
    if 'TTL' in dct:
        return(dct['TTL'])
        

def client(ip, port, message):
#    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    try:
#        sock.connect((ip, port))
#    except socket.error as err:
#        logging.error(err)
#        sys.exit(2)
#    sock.sendall(message)
#    sock.settimeout(5.0)
#    try:
#        msg = sock.recv(1024)
#    except socket.timeout:
#        logging.error("Connection to server timed out")
#        return 2
    # decode the JSON slaves
    msg_slaves = json.loads('{"UPDATE": true, "SLAVES": ["145.100.108.229", "145.100.108.234", "145.100.108.233", "145.100.108.230"], "TTL": 3600}', object_hook=parse_slaves)
    logging.info("Slaves: %s", msg_slaves)
    # decode the JSON TTL
    msg_ttl = json.loads('{"UPDATE": true, "SLAVES": ["145.100.108.229", "145.100.108.234", "145.100.108.233", "145.100.108.230"], "TTL": 3600}', object_hook=parse_ttl)
    logging.info("TTL: %s", msg_ttl)
    #for key, value in msg_decoded.iteritems():
    for item in msg_decoded:
        logging.info(item)
        if key == 'UPDATE':
            for slave in value:
                check_node(slave)
        if key == 'TTL':
            logging.info("Setting TTL to %s", value)
        if key == 'ERROR':
            logging.error("Server returned an ERROR message")

def check_node(ip):
    subprocess.check_call("ping -c 3 %s" % (IP),shell=True)

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
    # start logging 
    logformat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log.basicConfig(format=logformat, level=loglevel)
    # start connecting to server
    while 1:
        client(ip, port, "hello")

if __name__ == "__main__":
    main(sys.argv[1:])
