#!/usr/bin/python -Btt

import sys
import getopt
from time import sleep
from socket import *
import hashlib
import pickle
import json
import MySQLdb
import time

#defaults
BUFF = 1024
HOST = '0.0.0.0'
PORT = 1337
usedb = 0
db = MySQLdb.connect('localhost', 'root', 'geefmefietsterug', 'nlnog') 
cursor = db.cursor()

groupsize = 1
verbose = 0
nodelist = []
slavelists = []

def usage():
    print("Usage: decard-server -g[roup] 5 -v[erbose]\n"
        "-g[roup] 5     *The group size, default is 5\n"
        "-v[erbose]     *Verbose mode"
        "-d[atabase]    *Use a database (db config is in the script)"
    )
    sys.exit(2)

def sendmsg(ip, message):
    global PORT
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect((ip, PORT))
        sock.sendall(message)
        sock.close()
        #sock.settimeout(5.0)
        #response = sock.recv(1024)
        #print("Received: {}".format(response))
    except:
        print 'failed to send the master an update'

#Return the folowing $groupsize$ nodes as slaves to the client
def assign_slaves(clientsock, addr, data, hashed_addr):
    global groupsize
    global nodelist
    if verbose == 1:
        print 'Assigning the following ' + str(groupsize) + ' nodes to ' + addr[0]
    slavelist = []
    index_self = nodelist.index((hashed_addr, addr[0]))
    print(groupsize)
    for teller in range(0, groupsize):
        index_next = index_self + teller + 1
        #create a ring
        if index_next >= len(nodelist):
            index_next = index_next - len(nodelist)
            #when we looped the ring then it can occur that we see ourselves again, stop that!
            if index_next == index_self:
                if verbose == 1:
                    print 'We looped the entire ring' 
                break
        print nodelist[index_next]
        slavelist.append(nodelist[index_next])
    if verbose == 1:
        print 'Sending message: UPDATE ' + str(slavelist)
    #starting to send update the dictionary encoded in a JSON
    message = {'UPDATE': slavelist}
    message = json.dumps(message)
    clientsock.send(json.dumps(message))

#Return the folowing $groupsize$ nodes as masters to the client, and update their slave lists
def update_masters(clientsock, addr, data, hashed_addr, hello):
    global groupsize
    global nodelist
    if verbose == 1:
        print 'Updating the ' + str(groupsize) + ' nodes to be a master for ' + addr[0]
    index_self = nodelist.index((hashed_addr, addr[0]))
    for teller in range(0, groupsize):
        index_previous = index_self - teller - 1
        #create a ring
        if index_previous <= 0 - len(nodelist):
            index_previous = index_previous + len(nodelist)
            #when we looped the ring then it can occur that we see ourselves again, stop that!
            if index_previous == index_self:
                if verbose == 1:
                    print 'We looped the entire ring' 
                break
        #was this a hello or goodbye?
        if hello == 1:
            if verbose == 1:
                print 'Sending an update to master to ADD node: '
            sendmsg(nodelist[index_previous][1], 'ADD: ' + str(hashed_addr) + ', ' + str(nodelist[index_self][1] + '; ' + str(groupsize)))
        else:
            if verbose == 1:
                index_lastslave = index_self + groupsize
                if index_lastslave >= len(nodelist):
                    index_lastslave = index_lastslave - len(nodelist)
                print 'Sending an update to master to REPLACE node: '
            sendmsg(nodelist[index_previous][1], 'REPLACE: ' + str(hashed_addr) + ', ' + str(nodelist[index_self][1] + '; ' + str(nodelist[index_lastslave][0] + ', ' + str(nodelist[index_lastslave][1]))))

#handles an incomming hello message
def hello_handler(clientsock, addr, data):
    global nodelist
    global usedb
    global db
    global cursor

    #Check if you are already in the nodelist
    if verbose == 1:
        print 'Recieved a HELLO from ' + addr[0] + ', checking if we already know this host'
    for node in nodelist:
        if addr[0] in node:
            if usedb == 0:
                if verbose == 1:
                    print addr[0] + ' is already known, aborting'
                clientsock.send('ERROR: You are already known')
                return
            else:
                if verbose == 1:
                    print addr[0] + ' is a known host, We will allow him'
                    print "REPLACE INTO machinestates SET master_id=1, slave_id=(SELECT id FROM machines WHERE v4='" + addr[0] + "'), active=1, tstamp=" + str(int(time.time()))
                #update the database that we have seen him
                cursor.execute("REPLACE INTO machinestates SET master_id=1, slave_id=(SELECT id FROM machines WHERE v4='" + addr[0] + "'), active=1, tstamp=" + str(int(time.time())))
                db.commit()
                assign_slaves(clientsock, addr, data, hashed_addr)
    if usedb == 0:
        #Hash the new node's ip address and put it in the node_list
        if verbose == 1:
            print addr[0] + ' is a new node, proceeding with hashing'
        hashed_addr = hashlib.sha1(addr[0]).hexdigest()
        nodelist.append((hashed_addr, addr[0]))
        nodelist = sorted(nodelist)
        if verbose == 1:
            for node in nodelist:
                print node
        assign_slaves(clientsock, addr, data, hashed_addr)
    #update_masters(clientsock, addr, data, hashed_addr, 1) #1 means that this node sent a hello

    #Send an update to the $groupsize$ nodes before the new node to inform them that they have a new slave

#handles an incomming goodbye message
def goodbye_handler(clientsock, addr, data):
    global nodelist
    global db
    global cursor
    if verbose == 1:
        print 'Recieved a GOODBYE from ' + addr[0] + ', checking if we actually know this host'
    for node in nodelist:
        if addr[0] in node:
            if verbose == 1:
                print addr[0] + ' has been found'
            #now send an update to the masters to remove this node, and add new node: node[self_index + groupsize]  
            if usedb == 1:
                print addr[0] + ' is a known host, We will set him to unactive'
                print "REPLACE INTO machinestates SET master_id=1, slave_id=(SELECT id FROM machines WHERE v4='" + addr[0] + "'), active=0, tstamp=" + str(int(time.time()))
                #update the database that we have seen him
                cursor.execute("REPLACE INTO machinestates SET master_id=1, slave_id=(SELECT id FROM machines WHERE v4='" + addr[0] + "'), active=0, tstamp=" + str(int(time.time())))
                db.commit()
            #update_masters(clientsock, addr, data, node[0], 0) #0 means that this node sent a goodbye
            #nodelist.pop(node)
            return
    clientsock.send('ERROR: you were not part of the ring, you rowdy ruffian you')

#handles an incomming update message
def update_handler(clientsock, addr, data):
    clientsock.send('thank you for updating')
    if verbose == 1:
        print 'sent: I will update stuff now '

#handles an incomming message
def message_handler(clientsock, addr):
    while 1:
        data = clientsock.recv(BUFF)
        if verbose == 1:
            print 'data: ' + str(data)
        if not data: break

        #the recieved message decider
        if str(data) == 'hello':
            hello_handler(clientsock, addr, data)
        if str(data) == 'goodbye':
            goodbye_handler(clientsock, addr, data)
        if 'update' in str(data):
            update_handler(clientsock, addr, data)

def main(argv):
    global verbose
    global groupsize
    global nodelist
    global slavelists
    global usedb
    global cursor
    try:
        opts, args = getopt.getopt(argv, "hg:vd", ['help', 'group=', 'verbose', 'database'])
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-g", "--group"):
            groupsize = int(arg)
        elif opt in ("-v", "--verbose"):
            verbose = 1
        elif opt in ("-d", "--database"):
            usedb = 1

    # When using a database we can already fill in our nodelist
    if usedb == 1:
        if verbose == 1:
                print 'Contacting the database to fill up the node list, proceeding with hashing the hostname'
        cursor.execute('SELECT * FROM machines WHERE deckardserver IS NULL OR deckardserver = 0')
        data = cursor.fetchall()
        for node in data:
            hashed_addr = hashlib.sha1(node[1]).hexdigest()
            nodelist.append((hashed_addr, node[2]))
        nodelist = sorted(nodelist)
        if verbose == 1:
            for node in nodelist:
                print node

        #now generate the slave lists
        for (index_self, node) in enumerate(nodelist):
            slavelist.append
            if verbose == 1:
                print 'Assigning the following ' + str(groupsize) + ' nodes to ' + node[1]
            for teller in range(0, groupsize):
                index_next = index_self + teller + 1
                #create a ring
                if index_next >= len(nodelist):
                    index_next = index_next - len(nodelist)
                #when we looped the ring then it can occur that we see ourselves again, stop that!
                if index_next == index_self:
                    if verbose == 1:
                        print 'We looped the entire ring' 
                    break
                print nodelist[index_next]
                slavelists[index_self].append(nodelist[index_next])
    exit()
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

if __name__ == '__main__':
    main(sys.argv[1:])
