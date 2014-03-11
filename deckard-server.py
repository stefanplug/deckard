#!/usr/bin/python -Btt

import sys
import getopt
from time import sleep
from socket import *
import thread

#defaults
BUFF = 1024
HOST = '0.0.0.0'
PORT = 1337

groupsize = 5
verbose = 0

def usage():
	print("Usage: decard-server -g[roup] 10 -v[erbose]\n"
		"-g[roup] 5 	*The group size, default is 5\n"
		"-v[erbose] 		*Verbose mode"
	)
	sys.exit(2)

def hello_handler(clientsock, addr, data):
	clientsock.send('a slave list for you, use tests [PING, PORTSCAN, SSH]')
	print addr
	print verbose
	if verbose == 1:
		print 'sent: a slave list for you'

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
	while 1:
		if verbose == 1:
			print 'staying a while, and listening...'
		clientsock, addr = serversock.accept()
		thread.start_new_thread(message_handler, (clientsock, addr))

if __name__ == '__main__':
	main(sys.argv[1:])
