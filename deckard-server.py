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
import random

#defaults
BUFF = 1024
HOST = '0.0.0.0'
PORT = 1337
db = MySQLdb.connect('localhost', 'root', 'geefmefietsterug', 'nlnog') 
cursor = db.cursor()

timer = 10
groupsize = 5
verbose = 0
nodelist = []   #(hashed IPv4, IPv4, recieved a HELLO this lifetime?) lifetime resets when this service resets, we can use this to send a node the entire new slave when this service reloads list when it just sends us an update
slavelists = [] #(Master IP, Slave1 IP, Slave2 IP, ......, SlaveN IP)

def usage():
    print("Usage: decard-server -g[roup] 5 -v[erbose]\n"
        "-g[roup] 5         *The group size, default is 5\n"
        "-v[erbose]         *Verbose mode"
        "-t[imer] seconds    *The time between hashes, default is 3600 (1 hour)"
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

def generate_nodelist(salt):
    global nodelist
    del nodelist
    
    #get the node list form the database
    if verbose == 1:
        print 'Contacting the database to fill up the node list, proceeding with hashing the hostname'
    cursor.execute('SELECT * FROM machines WHERE deckardserver IS NULL OR deckardserver = 0')
    data = cursor.fetchall()
    #create a hashed nodelist and sort the list
    for node in data:
        hashed_addr = hashlib.sha1(str(salt) + node[1]).hexdigest()
        nodelist.append([hashed_addr, node[2], 0])
    nodelist = sorted(nodelist)
    if verbose == 1:
        for node in nodelist:
            print node
    return 0

def generate_slavelists():
    global nodelist
    global slavelists
    for (index_self, node) in enumerate(nodelist):
        slavelist = [node[1]]
        for teller in range(0, groupsize):
            index_next = index_self + teller + 1
            #create a ring
            if index_next >= len(nodelist):
                index_next = index_next - len(nodelist)
            #when we looped the ring then it can occur that we see ourselves again, stop that!
            if index_next == index_self:
                break
            slavelist.append(nodelist[index_next][1])
        slavelists.append(slavelist)

    if verbose == 1:
        print 'We came up with the following slave list:' 
        for slavelist in slavelists:
            print slavelist
    return 0

#handles an incomming hello message
def hello_handler(clientsock, addr, data):
    global nodelist
    global slavelists
    global db
    global cursor

    #Check if you are already in the nodelist
    if verbose == 1:
        print 'Recieved a HELLO from ' + addr[0] + ', checking if we know this host'
    for index_self, node in enumerate(nodelist):
        if addr[0] in node:
            if verbose == 1:
                print addr[0] + ' is a known host, We will allow him'
                print "REPLACE INTO machinestates SET master_id=1, slave_id=(SELECT id FROM machines WHERE v4='" + addr[0] + "'), active=1, tstamp=" + str(int(time.time()))
            #update the database that we have seen him
            cursor.execute("REPLACE INTO machinestates SET master_id=1, slave_id=(SELECT id FROM machines WHERE v4='" + addr[0] + "'), active=1, tstamp=" + str(int(time.time())))
            db.commit()
            #look up this nodes slaves
            print 'this nodes slaves are:'
            for slaves in slavelists[index_self]:
                print slaves
            #SEND SLAVELIST?
            #starting to send update the dictionary encoded in a JSON
            #message = {'UPDATE': slavelist}
            #message = json.dumps(message)
            #clientsock.send(json.dumps(message))

            #now update the node list to show that this node has been seen by us
            node[2] = 1
            return 0
    
    #the check must have been unsuccessfull because the for loop ended
    if verbose == 1:
        print addr[0] + ' is an unknown host, ignore!'
    return 1

#handles an incomming goodbye message
def goodbye_handler(clientsock, addr, data):
    global nodelist
    global db
    global cursor
    if verbose == 1:
        print 'Recieved a GOODBYE from ' + addr[0] + ', checking if this is a known host'
    for node in nodelist:
        if addr[0] in node:
            if verbose == 1:  
                print addr[0] + ' is a known host, We will set him to unactive'
                print "REPLACE INTO machinestates SET master_id=1, slave_id=(SELECT id FROM machines WHERE v4='" + addr[0] + "'), active=0, tstamp=" + str(int(time.time()))
            #update the database that we have seen him
            cursor.execute("REPLACE INTO machinestates SET master_id=1, slave_id=(SELECT id FROM machines WHERE v4='" + addr[0] + "'), active=0, tstamp=" + str(int(time.time())))
            db.commit()
            #now update the node list to show that this node has left
            node[2] = 0
            return 0

    #the check must have been unsuccessfull because the for loop ended
    if verbose == 1:
        print addr[0] + ' is an unknown host, ignore!'
    return 1

#handles an incomming update message
def update_handler(clientsock, addr, data):
    global nodelist
    global db
    global curso
    if verbose == 1:
        print 'Recieved an UPDATE from ' + addr[0] + ', checking if we know this host'
    for node in nodelist:
        if addr[0] in node:
            if verbose == 1:  
                print addr[0] + ' is a known host, lets see what it has to say'
            #update the database with this nodes findings
            seen = '1' #temp, get from update massage
            slaveaddr = '145.100.108.232' #temp, get from update message
            if verbose == 1:
                print "REPLACE INTO machinestates SET master_id=(SELECT id FROM machines WHERE v4='" + addr[0] + "') , slave_id=(SELECT id FROM machines WHERE v4='" + slaveaddr + "'), active=" + seen + ", tstamp=" + str(int(time.time()))
            cursor.execute("REPLACE INTO machinestates SET master_id=(SELECT id FROM machines WHERE v4='" + addr[0] + "') , slave_id=(SELECT id FROM machines WHERE v4='" + slaveaddr + "'), active=" + seen + ", tstamp=" + str(int(time.time())))
            db.commit()
            # Now lets see if this host needs a new slave list
            if node[2] == 0:
                if verbose == 1:  
                    print addr[0] + ' Needs a new slavelist, lets send it to the HELLO message handler'
                hello_handler(clientsock, addr, data)
            return 0

    #the check must have been unsuccessfull because the for loop ended
    if verbose == 1:
        print addr[0] + ' is an unknown host, ignore!'
    return 1

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
    global cursor
    try:
        opts, args = getopt.getopt(argv, "hg:v", ['help', 'group=', 'verbose'])
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-g", "--group"):
            groupsize = int(arg)
        elif opt in ("-v", "--verbose"):
            verbose = 1

    
    #start being a deckard server
    ADDR = (HOST, PORT)
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind(ADDR)
    serversock.listen(5)

    generate_nodelist(random.random())
    generate_slavelists()
    end_time = time.time() + timer
    if verbose == 1:
        print 'staying a while, and listening...'
    while 1:
        if time.time() > end_time:
            if verbose == 1:
                print 'The time has come to assign new slaves'
            generate_nodelist(random.random())
            generate_slavelists()
            end_time = time.time() + timer
        else:
            clientsock, addr = serversock.accept()
            message_handler(clientsock, addr)

if __name__ == '__main__':
    main(sys.argv[1:])
