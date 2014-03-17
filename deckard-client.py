#!/usr/bin/python3
#import ConfigParser
import sys
import getopt
import socket
import subprocess
import json
import logging
import time
from multiprocessing import Pool

def usage():
    print("Usage: decard-client -s 127.0.0.1 -p 1337\n\n"
        "\t-s[erver] 127.0.0.1     *IP address\n"
        "\t-p[ort] 1337            *Port number\n"
        "\t-v                      *Verbose mode\n"
    )
    sys.exit(2)

def parse_type(dct):
    if 'UPDATE' in dct:
        return('UPDATE')
    elif 'ERROR' in dct:
        return('ERROR')
    else:
        return("UNKOWN")

def parse_slaves(dct):
    if 'SLAVES' in dct:
        return(dct['SLAVES'])

def parse_ttl(dct):
    if 'TTL' in dct:
        return(dct['TTL'])
        
def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, port))
    except socket.error as err:
        logging.error(err)
        sys.exit(2)
    sock.sendall(message.encode())
    sock.settimeout(5.0)
    try:
        msg = sock.recv(1024).decode()
    except socket.timeout:
        logging.error("Connection to server timed out")
        return 2
    # for testing purposes
    #msg = '{"ERROR": true}'
    #msg = '{"UPDATE": true, "SLAVES": ["145.100.108.229", "145.100.108.234", "145.100.108.233", "145.100.108.230"], "TTL": 3600}'
    # decode the JSON message type
    msg_type = json.loads(msg, object_hook=parse_type)
    logging.info("Message type: %s", msg_type)

    if msg_type == 'UPDATE':
        # decode the JSON slaves
        logging.info(msg)
        msg_slaves = json.loads(msg, object_hook=parse_slaves)
        logging.info("Slaves: %s", msg_slaves)
        # decode the JSON TTL
        msg_ttl = json.loads(msg, object_hook=parse_ttl)
        logging.info("TTL: %s", msg_ttl)


        #pool = Pool(processes=4)               # start 4 worker processes
        #result = pool.apply_async(f, [10])     # evaluate "f(10)" asynchronously
        #print(result.get(timeout=1))           # prints "100" unless your computer is *very* slow
        #print(pool.map(f, range(10)))          # prints "[0, 1, 4,..., 81]"

        for slave in msg_slaves:
            status = check_node(slave)
            if status == False:
                notify(slave)
    else:
        logging.info("unkown message")
        
def check_node(ip):
    """
    This function determines if a node is up or not. In here
    you should define the "availability" tests.

    TODO: multiprocessing?
    """
    ping = subprocess.call("ping -c 2 %s" % ip, shell=True)
    logging.info("ping return code: %i", ping)
    if ping == 0:
        return(True)
    if ping == 1:
        logging.error("ping return code: %i", ping)
        return(False)

def notify(slave):
    """
    Notify the Deckard-server that a node is unavailable from our
    perspective.
    """
    message = {'UPDATE': 'true', slave, 'STATUS': 0}
    message = json.dumps(message)
    try:
        sock.connect((ip, port))
    except socket.error as err:
        logging.error(err)
        sys.exit(2)
    sock.sendall(message.encode())
    sock.settimeout(5.0)
    try:
        msg = sock.recv(1024).decode()
    except socket.timeout:
        logging.error("Connection to server timed out")
        return 2

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
    logformat = "%(asctime)s - %(levelname)s - %(message)s"
    log.basicConfig(format=logformat, level=loglevel)
    # start connecting to server
    while 1:
        client(ip, port, "hello")
        time.sleep(1)

if __name__ == "__main__":
    main(sys.argv[1:])
