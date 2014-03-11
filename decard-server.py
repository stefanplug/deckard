#!/usr/bin/python -Btt

import sys
import getopt
from Crypto.Cipher import AES
from Crypto import Random
from base64 import b64encode
from base64 import b64decode
from time import sleep
from scapy.all import *

#sean is de beste

def usage():
	print("Usage: decard-server -g[roup]\n"
		"-g[roup] 5 *The group size, default is 5\n"
	)
	sys.exit(2)

def main(argv):
	try:
		opts, args = getopt.getopt(argv, "g:", ["help", 'group='])
	except getopt.GetoptError:
		usage()

	#defaults
	groupsize = 5

	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
		elif opt in ("-g", "--group"):
			groupsize = arg

	#start being a deckard server
	while 1:
		msg = listen()
		print msg

#Listen for Decard nodes
def listen():
	msg = []
	while 1:
		recieved = sniff(filter="tcp and port 1337", count=1)
			return str(msg)

def byte_converter(x, size):
	teller = len(x) - (len(x) * 2)
	output = ['0' for y in range(size)]
	for c in x:
		output[teller] = c
		teller = teller + 1
	return output

msglist = [['*' for y in range(22)] for x in range(4096)]
def recieve_dip6(network, netmask):
	while 1:
		#filt = lambda (r): r[IP].src == '192.168.1.1'
		#recieved = sniff(filter=ip6, count=1)
		recieved = sniff(filter='net '+ network + '/' + netmask, count=3)
		#data = recieved[0].payload.dst.split(':')
		try:
			data = recieved[2].payload.dst.split(':')
		except:
			print 'recieved a bad destination address'

		try:
			control = byte_converter(data[-2], 4)
			msgid = int("".join(control[0:2]), 16)
			seq = int("".join(control[2:]), 16)
			if not '*' in "".join(msglist[msgid]):
				print 'We already know this message, Ignoring'
			else:
				data = byte_converter(data[-1], 4)
				B1 = chr(int("".join(data[0:2]), 16))
				B2 = chr(int("".join(data[2:]), 16))
				msglist[msgid][seq] = B1+B2
				print 'message #'+ str(msgid) +': '+ "".join(msglist[msgid])
				if not '*' in "".join(msglist[msgid]):
					msg = [msgid, "".join(msglist[msgid])]
					return msg
		except:
			print 'recieved invalid dst IP, ignoring'

def send_sp(msg, ipv6_dst):
	packet = IPv6(dst=ipv6_dst)
	segment = TCP(dport=80, flags=0x02)
	print msg
	for c in msg:
		segment = TCP(sport = ord(c) + 10000)
		send(packet/segment)
		sleep(1)
	segment = TCP(sport = 30000)
	send(packet/segment)

def send_dip6(msgid, msg, network, sourceip):
	segment = TCP(dport=80, sport=RandNum(1024, 65535), flags=0x02)
	print network
	for i in range(2):
		if network[-1] == ':':
			network = network[:-1]
	print msgid, msg
	teller = 0

	msgid = '%x' % msgid
	msgid = byte_converter(msgid, 2)
	for seq in range(22):
		dest = [':']
		seq = '%x' % seq
		seq = byte_converter(seq, 2)
		dest = dest + msgid + seq + [':']

		B1 = '%x' % ord(msg[teller])
		B1 = byte_converter(B1, 2)
		teller = teller + 1
		B2 = '%x' % ord(msg[teller])
		B2 = byte_converter(B2, 2)
		teller = teller + 1
		dest = dest + B1 + B2
		
		print network + "".join(dest)
		packet = IPv6(src = sourceip, dst = network + "".join(dest))
		#packet = IPv6(dst = network + "".join(dest))
		send(packet/segment)
		sleep(1)

def encrypt(key, clear):
	BLOCK_SIZE = 32
	PADDING = '/'
	pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
	EncodeAES = lambda c, s: b64encode(c.encrypt(pad(s)))
	cipher = AES.new(key)
	msg = EncodeAES(cipher, clear)
	return msg

def decrypt(key, msg):
	BLOCK_SIZE = 32
	PADDING = '/'
	pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
	DecodeAES = lambda c, e: c.decrypt(b64decode(e)).rstrip(PADDING)
	cipher = AES.new(key)
	try:
		clear = DecodeAES(cipher, msg[1])
	except:
		print 'corrupt message, ignoring'
		for y in range(22):
			msglist[msg[0]][y] = '*'
		return -1
	return clear

if __name__ == '__main__':
	main(sys.argv[1:])
