#!/usr/bin/python3 -Btt

import sys
import getopt
from time import sleep
from socket import *
import hashlib
import pickle
import json
#import MySQLdb
import mysql.connector
import time
import random

#nodelist and slavelists makeup:
#nodelist[Ha5H, 192.168.1.1, 0]   #(hashed IPv4, IPv4, hash_epoch) When node send an update and the hash_epoch is 0 then it will get a new slave list from the server
#slavelists[[Master IP1, Slave1 IP, Slave2 IP, ......, SlaveN IP], [Master IP2, Slave1 IP, Slave2 IP, ......, SlaveN IP]] # a list of lists conaining a master IP with its assigned slave ips

#defaults
BUFF = 1024
V4HOST = '0.0.0.0'
V6HOST = '::'
PORT = 1337
#db = MySQLdb.connect('localhost', 'root', 'geefmefietsterug', 'nlnog') 
db = mysql.connector.connect(user='root', password='geefmefietsterug', host='localhost', database='nlnog') 
cursor = db.cursor()

protocol = 0
timer = 3600
groupsize = 5
verbose = 0
stale_multiplier = 5    #h(if time = 10 seconds and the multiplier = 5, then any record older than 50 seconds is stale)

def usage():
    print("Usage: decard-server -p 4 -g 5 -t 3600 -s 5 -v\n"
        "-p[rotocol] 4 or 6     *Use ipv4 or ipv6? **Required**\n"
        "-g[roup] 5             *The group size, default is 5\n"
        "-t[imer] seconds       *The time between hashes, default is 3600 (1 hour)\n"
        "-s[tale] 5             *The numer of timer times before update data is considered stale\n"
        "-v[erbose]             *Verbose mode\n"
    )
    sys.exit(2)

def ttl_formula(timer):
    timer = timer / 2 + 1
    return timer

def stale_record_formula(timer):
    global stale_multiplier
    oldage = timer * stale_multiplier
    stale_time = time.time() - oldage
    return stale_time

def generate_nodelist(salt, protocol):
    nodelist = []
    #get the node list form the database
    if verbose == 1:
        print('Contacting the database to fill up the node list, proceeding with hashing the hostname')
    if protocol == 4:
        cursor.execute('SELECT (v4) FROM machines WHERE (deckardserver IS NULL OR deckardserver = 0) AND v4 IS NOT NULL')
    else:
        cursor.execute('SELECT (v6) FROM machines WHERE (deckardserver IS NULL OR deckardserver = 0) AND v6 IS NOT NULL')
    data = cursor.fetchall()
    #create a hashed nodelist and sort the list
    for node in data:
        hashed_addr = hashlib.sha1(str(salt).encode('utf-8') + node[0].encode('utf-8')).hexdigest()
        #hashed_addr = hashlib.sha1(salt).hexdigest
        nodelist.append([hashed_addr, str(node[0]), 0])
    nodelist = sorted(nodelist)
    if verbose == 1:
        for node in nodelist:
            print(node)
    return nodelist

def generate_slavelists(nodelist):
    slavelists = []
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
        print('We came up with the following slave list:') 
        for slavelist in slavelists:
            print(slavelist)
    return slavelists

#handles an incomming hello message
def hello_handler(clientsock, addr, data, nodelist, slavelists, protocol):
    global db
    global cursor

    #Check if you are already in the nodelist
    if verbose == 1:
        print('Recieved a HELLO from ' + addr[0] + ', checking if we know this host')
    for index_self, node in enumerate(nodelist):
        if addr[0] in node:
            if verbose == 1:
                print(addr[0] + ' is a known host, We will allow him')
            #update the database that we have seen him
            if protocol == 4:
                cursor.execute("REPLACE INTO machinestates SET master_id=1, slave_id=(SELECT id FROM machines WHERE v4='" + addr[0] + "'), protocol=4, active=1, tstamp=" + str(int(time.time())))
            else:
                cursor.execute("REPLACE INTO machinestates SET master_id=1, slave_id=(SELECT id FROM machines WHERE v6='" + addr[0] + "'), protocol=41, active=1, tstamp=" + str(int(time.time())))
            db.commit()
            #look up this nodes slaves
            if verbose == 1:
                print('this nodes slaves are:')
                for slaves in slavelists[index_self]:
                    print(slaves)

            #Send the slave list PLUS a TTL to the node
            ttl = ttl_formula(timer)
            message = {b'UPDATE': 'true', 'SLAVES': slavelists[index_self], 'TTL': ttl}
            message = json.dumps(message)
            clientsock.send(json.dumps(message))

            #now update the node list to show that this node has been seen by us
            node[2] = 1
            return 0
    
    #the check must have been unsuccessfull because the for loop ended
    if verbose == 1:
        print(addr[0] + ' is an unknown host, ignore!')
    return 1

#handles an incom0ming goodbye message
def goodbye_handler(clientsock, addr, data, nodelist, slavelists, protocol):
    global db
    global cursor
    if verbose == 1:
        print('Recieved a GOODBYE from ' + addr[0] + ', checking if this is a known host')
    for node in nodelist:
        if addr[0] in node:
            if verbose == 1:  
                print(addr[0] + ' is a known host, We will set him to unactive')
            #update the database that we have seen him
            if protocol == 4:
                cursor.execute("REPLACE INTO machinestates SET master_id=1, slave_id=(SELECT id FROM machines WHERE v4='" + addr[0] + "'), protocol = 4, active=0, tstamp=" + str(int(time.time())))
            else:
                cursor.execute("REPLACE INTO machinestates SET master_id=1, slave_id=(SELECT id FROM machines WHERE v6='" + addr[0] + "'), protocol=41, active=0, tstamp=" + str(int(time.time())))
            db.commit()
            #now update the node list to show that this node has left
            node[2] = 0
            return 0

    #the check must have been unsuccessfull because the for loop ended
    if verbose == 1:
        print(addr[0] + ' is an unknown host, ignore!')
    return 1

#handles an incomming update message
def update_handler(clientsock, addr, data, nodelist, slavelists, protocol):
    global db
    global cursor
    if verbose == 1:
        print('Recieved an UPDATE from ' + addr[0] + ', checking if we know this host')
    for node in nodelist:
        if addr[0] in node:
            if verbose == 1:  
                print(addr[0] + ' is a known host, lets see what it has to say')
            #update the database with this nodes findings
            seen = '1' #temp, get from update massage
            slaveaddr = '145.100.108.232' #temp, get from update message
            if protocol == 4:
                cursor.execute("REPLACE INTO machinestates SET master_id=(SELECT id FROM machines WHERE v4='" + addr[0] + "') , slave_id=(SELECT id FROM machines WHERE v4='" + slaveaddr + "'), protocol=4, active=" + seen + ", tstamp=" + str(int(time.time())))
            else:
                cursor.execute("REPLACE INTO machinestates SET master_id=(SELECT id FROM machines WHERE v6='" + addr[0] + "') , slave_id=(SELECT id FROM machines WHERE v6='" + slaveaddr + "'), protocol=41, active=" + seen + ", tstamp=" + str(int(time.time())))
            db.commit()

            #update the slave's status 
            if verbose == 1:
                print('See if the supdate has changed anything for the slaves status')
            stale_record_time = stale_record_formula(timer)
            if protocol == 4:
                cursor.execute("SELECT COUNT(*) FROM machinestates WHERE slave_id=(SELECT id FROM machines WHERE v4='" + slaveaddr + "') AND protocol=4 AND active=1 AND tstamp >"+ stale_record_time)
            else:
                cursor.execute("SELECT COUNT(*) FROM machinestates WHERE slave_id=(SELECT id FROM machines WHERE v6='" + slaveaddr + "') AND protocol=41 AND active=1 AND tstamp >"+ stale_record_time)
            active_count = cursor.fetchall()
            if protocol == 4:
                cursor.execute("SELECT COUNT(*) FROM machinestates WHERE slave_id=(SELECT id FROM machines WHERE v4='" + slaveaddr + "') AND protocol=4 AND active=0 AND tstamp >"+ stale_record_time)
            else:
                cursor.execute("SELECT COUNT(*) FROM machinestates WHERE slave_id=(SELECT id FROM machines WHERE v6='" + slaveaddr + "') AND protocol=41 AND active=0 AND tstamp >"+ stale_record_time)
            inactive_count = cursor.fetchall()
            if (inactive_count == 0) and (active_count > 0):
                if verbose == 1:
                    print('This slave was found to be active')
                if protocol == 4:
                    cursor.execute("REPLACE INTO machines SET v4active=1 WHERE v4='" + slaveaddr + "'")
                else:
                    cursor.execute("REPLACE INTO machines SET v6active=1 WHERE v6='" + slaveaddr + "'")
                db.commit()
            elif (inactive_count > 0) and (active_count == 0):
                if verbose == 1:
                    print('This slave was found to be inactive')
                if protocol == 4:
                    cursor.execute("REPLACE INTO machines SET v4active=0 WHERE v4='" + slaveaddr + "'")
                else:
                    cursor.execute("REPLACE INTO machines SET v6active=0 WHERE v6='" + slaveaddr + "'")
                db.commit()
            else:
                if verbose == 1:
                    print('This slave was found to be active for some nodes, but inactive for others')
                if protocol == 4:
                    cursor.execute("REPLACE INTO machines SET v4active=2 WHERE v4='" + slaveaddr + "'")
                else:
                    cursor.execute("REPLACE INTO machines SET v6active=2 WHERE v6='" + slaveaddr + "'")
                db.commit()
            
            #lets see if this host needs a new slave list
            if node[2] == 0:
                if verbose == 1:  
                    print(addr[0] + ' Needs a new slavelist, lets send it to the HELLO message handler')
                hello_handler(clientsock, addr, data, nodelist, slavelists)
            return 0

    #the check must have been unsuccessfull because the for loop ended
    if verbose == 1:
        print(addr[0] + ' is an unknown host, ignore!')
    return 1

#handles an incomming message
def message_handler(clientsock, addr, nodelist, slavelists, protocol):
    data = clientsock.recv(BUFF)
    if verbose == 1:
        print(data)
    if not data: 
        return
    #the recieved message decider
    if data == b'hello':
        hello_handler(clientsock, addr, data, nodelist, slavelists, protocol)
    elif data == b'goodbye':
        goodbye_handler(clientsock, addr, data, nodelist, slavelists, protocol)
    elif 'update' in data:
        update_handler(clientsock, addr, data, nodelist, slavelists, protocol)
    else:
        print('Recieved an unknown packet type, ignore!')

def main(argv):
    global verbose
    global groupsize
    global cursor
    global protocol
    try:
        opts, args = getopt.getopt(argv, "hp:g:t:s:v", ['help', 'protocol=', 'group=', 'timer=', 'stale=', 'verbose'])
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-p", "--protocol"):
            protocol = int(arg)
            if (protocol != 4):
                if (protocol != 6):
                    usage()
        elif opt in ("-g", "--group"):
            groupsize = int(arg)
        elif opt in ("-t", "--timer"):
            timer = int(arg)
        elif opt in ("-s", "--stale"):
            stale_multiplier = int(arg)
        elif opt in ("-v", "--verbose"):
            verbose = 1
    if protocol == 0:
        usge()

    #start being a deckard server
    if protocol == 4:
        ADDR = (V4HOST, PORT)
        serversock = socket(AF_INET, SOCK_STREAM)
    else:
        ADDR = (V6HOST, PORT)
        serversock = socket(AF_INET6, SOCK_STREAM)
        serversock.setsockopt(IPPROTO_IPV6, IPV6_V6ONLY, 0)
    serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind(ADDR)
    serversock.listen(5)

    nodelist = generate_nodelist(random.random(), protocol)
    slavelists = generate_slavelists(nodelist)
    end_time = time.time() + timer
    if verbose == 1:
        print('staying a while, and listening...')
    while 1:
        if time.time() > end_time:
            if verbose == 1:
                print('The time has come to assign new slaves')
            nodelist = generate_nodelist(random.random(), protocol)
            slavelists = generate_slavelists(nodelist)
            end_time = time.time() + timer
        else:
            clientsock, addr = serversock.accept()
            message_handler(clientsock, addr, nodelist, slavelists, protocol)

if __name__ == '__main__':
    main(sys.argv[1:])
