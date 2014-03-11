#!/usr/bin/python -Btt

import sys
import getopt
from time import sleep
from socket import *
#import thread
#import threading
import hashlib

#defaults
BUFF = 1024
HOST = '0.0.0.0'
PORT = 1337

groupsize = 1
verbose = 0
nodelist = []

def usage():
    print("Usage: decard-server -g[roup] 10 -v[erbose]\n"
        "-g[roup] 5     *The group size, default is 5\n"
        "-v[erbose]         *Verbose mode"
    )
    sys.exit(2)

def hello_handler(clientsock, addr, data):
    global groupsize
    global nodelist

    #Check if you are already in the nodelist
    if verbose == 1:
        print 'Recieved a HELLO from ' + addr[0] + ', checking if we already know this host'
    for node in nodelist:
        if addr[0] in node:
            if verbose == 1:
                print addr[0] + ' is already known, aborting'
            clientsock.send('ERROR: You are already known')
            return

    #Hash the new node's ip address and put it in the node_list
    if verbose == 1:
        print addr[0] + ' is a new node, proceeding with hashing'
    hashed_addr = hashlib.sha1(addr[0]).hexdigest()
    nodelist.append((hashed_addr, addr[0]))
    nodelist = sorted(nodelist)
    if verbose == 1:
        for node in nodelist:
            print node

    #Return the folowing $groupsize$ nodes as slaves to the client
    if verbose == 1:
        print 'Assigning the following ' + str(groupsize) + ' nodes to ' + addr[0]
    slavelist = []
    index_self = nodelist.index((hashed_addr, addr[0]))
    print index_self
    for teller in range(0, groupsize):
        index_next = index_self + teller + 1
        #create a ring
        if index_next > len(nodelist):
            index_next = index_next - len(nodelist)
            #when we looped the ring then it can occur that we see ourselves again, stop that!
            if index_next == index_self:
                if verbose == 1:
                    print 'We looped the entire ring' 
                break
        print nodelist[index_next]

    clientsock.send('slavelist: lijstje; tests: [PING, PORTSCAN, SSH]')

def bye_handler(clientsock, addr, data):
    clientsock.send('I will remove you from the list and update the other servers')
    if verbose == 1:
        print 'sent: I will remove you from the list and update the other servers'

def update_handler(clientsock, addr, data):
    clientsock.send('I will update stuff now')
    if verbose == 1:
        print 'sent: I will update stuff now '

def message_handler(clientsock, addr):
    while 1:
        data = clientsock.recv(BUFF)
        if verbose == 1:
            print 'data: ' + str(data)
        if not data: break

        #the recieved message decider
        if str(data) == 'hello':
            hello_handler(clientsock, addr, data)
        if str(data) == 'bye':
            bye_handler(clientsock, addr, data)
        if 'update' in str(data):
            update_handler(clientsock, addr, data)

def main(argv):
    global verbose
    try:
        opts, args = getopt.getopt(argv, "hg:v", ['help', 'group=', 'verbose'])
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-g", "--group"):
            groupsize = arg
        elif opt in ("-v", "--verbose"):
            verbose = 1

    #start being a deckard server
    ADDR = (HOST, PORT)
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind(ADDR)
    serversock.listen(5)
    if verbose == 1:
        print 'staying a while, and listening...'
    while 1:
        clientsock, addr = serversock.accept()
        message_handler(clientsock, addr)
        #thread.start_new_thread(message_handler, (clientsock, addr))
        #thread = threading.Thread(target=message_handler, args=(clientsock, addr))
        #thread.start()

if __name__ == '__main__':
    main(sys.argv[1:])
