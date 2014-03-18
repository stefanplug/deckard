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

def sendmsg(sock, msg):
    timeout = 5.0
    sock.settimeout(timeout)
    try:
        sock.connect((ip, port))
    except socket.error as err:
        logging.error(err)
        return 2 
    finally:
        sock.sendall(msg.encode())
        sock.close()

def sendrecvmsg(sock, msg):
    timeout = 5.0
    sock.settimeout(timeout)
    try:
        sock.connect((ip, port))
    except socket.error as err:
        logging.error(err)
        quit(2)
    sock.sendall(msg.encode())
    try:
        msg = sock.recv(1024).decode()
        return msg
    except socket.timeout:
        logging.error("Connection to server timed out")
        return 2
    finally:
        sock.close()

def client(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    message = {'HELLO': 'true'}
    message = json.dumps(message)
    msg = sendrecvmsg(sock, message)
    sock.close()

    #parse message type
    msg_type = json.loads(msg, object_hook=parse_type)
    logging.debug("Message type: %s", msg_type)

    if msg_type == 'UPDATE':
        # decode the slaves list to a list
        logging.debug(msg)
        msg_slaves = json.loads(msg, object_hook=parse_slaves)
        logging.debug("Slaves: %s", msg_slaves)
        # decode the JSON TTL
        msg_ttl = json.loads(msg, object_hook=parse_ttl)
        logging.debug("TTL: %s", msg_ttl)

        #start availability checking in parallel
        logging.debug("Starting %i processes in 2 seconds", len(msg_slaves))
        time.sleep(2)
        pool = Pool(processes=len(msg_slaves))
        #remove ourself from the slave list
        msg_slaves.pop(0)
        for slave in msg_slaves:
            pool.Process(target=CheckNode, args=(ip, port, slave, msg_ttl)).start()
        pool.close()
        pool.join()
        logging.debug('Client function done')
    else:
        logging.debug("unkown message")

class CheckNode():
    """
    Check a slave nodes availability
    """
    def __init__(self, server_ip, server_port, slave, ttl):
        #the default mark is offline
        self.alive = 1
        self.ip = server_ip
        self.port = server_port
        self.ttl = ttl
        self.limit = self.ttl + time.time()
        #check the node until TTL
        while self.limit > time.time():
            self.check_node(slave)
            #WARNING: The below time should be depending on what scripts
            #         scripts you plan to run for availability checking.
            time.sleep(10)
        return None
    def check_node(self, slave):
        """
        This function determines if a node is up or not. In here
        you should define the "availability" tests.
        """
        ping = subprocess.call("ping -c 2 %s" % slave, shell=True)
        logging.info("ping return code: %i", ping)
        if (ping == 0) and (self.alive != 0):
            logging.warning("notifing deckard-server slave is alive again")
            notify_available(slave)
        elif self.alive != 1:
            logging.warning("notifing deckard-server slave is down again")
            notify_unvailable(slave)

def notify_available(slave):
    """
    Notify the Deckard-server that a node is available from our
    perspective.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    message = {'UPDATE': 'true', 'SLAVE': slave, 'STATUS': 1}
    message = json.dumps(message)
    sendmsg(sock, message)

def notify_unvailable(slave):
    """
    Notify the Deckard-server that a node is unavailable from our
    perspective.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    message = {'UPDATE': 'true', 'SLAVE': slave, 'STATUS': 0}
    message = json.dumps(message)
    sendmsg(sock, message)

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
    global ip
    global port
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
    # keep running forever
    while 1:
        client(ip, port)

if __name__ == "__main__":
    main(sys.argv[1:])
