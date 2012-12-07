#!/usr/bin/python

#alex plays with scapy after getting packets from tun

import logging
logging.getLogger("scapy").setLevel(1)
import subprocess
from scapy.all import *
import socket
import fcntl
import struct
import sys
import os
import select
import tornado.ioloop

import sniffing
import server

from threading import Thread

TUN_IP = '10.0.0.1' # we strip this off packet and replace source with our own source, but need to put back on packet upon return
# the port to use
SERVER_PORT =  6354 # 8081

"""For TCP, disable the kernel's response with:"""
subprocess.check_call('sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP', shell = True)
""" to set it back: """
#subprocess.check_call('sudo iptables -D OUTPUT -p tcp --tcp-flags RST RST -j DROP', shell = True)


# the event loop
ioloop = tornado.ioloop.IOLoop.instance()

node = None


def quit():
	global node
	node.stop()
	if (node.sniffer != None):
		node.sniffer.running = False
	ioloop.stop()
def stars():
	print('**********************************************************')

commands={\
'q':quit,
'quit':quit,
's':stars,
}
#^^^^^^^^^
# handlers
def stdinHandler(fd, events):
	buff = sys.stdin.readline().strip()
	try:
		commands[buff]()
	except KeyError:
		print('Command not recognized:'+buff)
		
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# int main(int argc, char** argv)
#
if __name__=='__main__':
	#global ioloop
	try:
		ioloop.add_handler(sys.stdin.fileno(), stdinHandler, ioloop.READ)
		node = Node()
		print('node initialized')
		node.start()
		print('node thread started')
		ioloop.start()
	except Exception, err:
		print("ERROR: "+str(err))
	finally:
		print('done with main')

""" I want there to be one item server-side that handles the reading from websocket (owns websocket) and also handles 
		the packet sniffing, ie, owns the SniffingThread.
		Since we've been building so many 'nodes', I named it 'node'...sorry
"""
class Node(Thread):
	def __init__(self):
		Thread.__init__(self)
		# Node owns the websocket -- let's give it a websocket
		self.application = tornado.web.Application([(r'/websocket', server.BasicWebSocket),])
		self.port_list = []
	
	def stop(self):
		self.sniffer.stopSniffing()
		
	def run(self):
		# start sniffing
		try:
			self.sniffer = sniffing.SniffingThread(self) #pass in reference to node
			self.sniffer.start()
		except Exception, err:
			print('Error: could not initialize sniffing thread: '+str(err))
			return
		# start listening
		try:
			self.application.listen(SERVER_PORT)
		except Exception, err:
			print('Error: could not initialize application and listen'+str(err))	
		# for now I'm sending one of our saved guys to start
		pkt = m(self, 'ip1.pkt')
		print('new port_list after calling m: '+str(self.port_list))
		send(pkt)
		print('sent packet: ')
		print(pkt)
	
	""" After SniffingThread gets a packet off the wire, it sends it back to node to be checked and handled """
	def handle_sniffed(self, pkt):
		if self.check_remembered(pkt):
			print('sniffed packet with sport: '+str(pkt.sport)+' and dport: '+str(pkt.dport))
	
	""" Our way to keep track of which packets are worth filtering when sniffing is to have a port_list:
			we keep list of ports of sent packets as tuple (sport, dport).
			When we get a new packet from client's tun, we save its port in list 
				so that when its response comes back we can put back the correct ip to return to client
		Returns modified port_list and packet
	"""
	def remember_packet(self, new_packet):
		#if (new_packet.sport not in port_list): --should we avoid storing more than once?
		self.port_list.append((new_packet.sport, new_packet.dport))
		return new_packet
	
	""" Returns True if packet's port pair is from client-tun, False otherwise.  
		Also modifies port_list by taking out pair.  """
	def check_remembered(self, packet):
		list = self.port_list
		if ((packet.dport, packet.sport) in list):
			self.port_list.remove((packet.dport, packet.sport))
			return True
		else:
			return False


""" Converts encoded string data from websocket, sent as message from client tun, into an IP packet (IP/TCP is what we're assuming we'll get)
	returns packet """
def msg_to_packet(file_name): #right now I have it in a file
	file = open(file_name)
	packet_string = file.read()
	# it was probably saved with a newline on it
	packet_string = packet_string.rstrip('\n')
	# we encoded packet in base64
	packet_string = packet_string.decode('base64')
	packet = IP(packet_string)
	file.close()
	return packet	

#def modify_send_packet_from_file(file_name):
def m(node, file_name):
	packet = msg_to_packet(file_name)
	node.remember_packet(packet)
	print 'original ip packet:'
	print('packet.src: '+str(packet.src))
	print('packet.dst: '+str(packet.dst))
	our_ip = get_ip('eth0')
	print('new packet src: '+our_ip)
	packet.src = our_ip
	# need to reset checksum
	packet = reset_checksum(packet)
	
	return packet

""" ******************** Helper Functions Below ************************* """

""" sample use: get_ip_address('eth0') returns '38.113.228.130' """
def get_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

""" Resets the checksum of the packet after packet minipulated
		 I think the only layers we deal with are ip and tcp 
	returns new packet with supposedly correct checksum """
def reset_checksum(packet):
	# first delete existing checksums
	if (packet.haslayer(TCP)):
		del(packet.getlayer(TCP).chksum)
	if (packet.haslayer(IP)):
		del(packet.getlayer(IP).chksum)
	# lets let scapy recalculate checksum:
	packet = packet.__class__(str(packet))
	return packet


	
	
