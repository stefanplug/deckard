#!/usr/bin/python -Btt

import sys
import getopt
from time import sleep
from socket import *
import thread

#sean is de beste

def usage():
	print("Usage: decard-server -g[roup]\n"
		"-g[roup] 5 *The group size, default is 5\n"
	)
	sys.exit(2)

def gen_response():
	return 'This is a Kite Shield of Eternal Verginity; +2 arcane magic defence'

def handler(clientsock, addr):
	while 1:
		data = clientsock.recv(BUFF)
		print 'data:' + repr(data)
		if not data: break
		clientsock.send(gen_response())
		print 'sent:' + repr(gen_response())
		clinetsock.close()

def main(argv):
	try:
		opts, args = getopt.getopt(argv, "g:", ["help", 'group='])
	except getopt.GetoptError:
		usage()

	#defaults
	groupsize = 5
	BUFF = 1024
	HOST = '127.0.0.1'
	PORT = 1337

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
		elif opt in ("-g", "--group"):
			groupsize = arg

	#start being a deckard server
	ADDR = (HOST, PORT)
	serversock = socket(AF_INET, SOCK_STREAM)
	serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	serversock.bind(ADDR)
	serversock.listen(5)
	while 1:
		print 'staying a while, and listening...'
		clientsock, addr = serversock.accept()
		print 'recieved a hello from:' + address_string
		thread.start_new_thread(handler, (clientsock, addr))

#Listen for Decard nodes
def listen():
	msg = []
	while 1:
		recieved = sniff(filter="tcp and port 1337", count=1)
		return str(msg)

if __name__ == '__main__':
	main(sys.argv[1:])
