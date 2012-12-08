import logging
logging.getLogger("scapy").setLevel(1)
import subprocess
from scapy.all import *
import socket
import fcntl
import struct
import tornado.ioloop
import sniffing
import BasicWebSocket 

from threading import Thread

packetToSniff='ipnew.pkt'

TUN_IP = '10.0.0.1' # we strip this off packet and replace source with our own source, but need to put back on packet upon return
# the port to use
SERVER_PORT =  6354

"""For TCP, disable the kernel's response with:"""
subprocess.check_call('sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP', shell = True)
""" to set it back: """
#subprocess.check_call('sudo iptables -D OUTPUT -p tcp --tcp-flags RST RST -j DROP', shell = True)

class Node():
	""" I want there to be one item server-side that handles the reading from websocket (owns websocket) and also handles 
		the packet sniffing, ie, owns the SniffingThread.
		Since we've been building so many 'nodes', I named it 'node'...sorry
	"""
	def __init__(self):
		self.ws			 = None
		self.application = tornado.web.Application([(r'/websocket',BasicWebSocket.BasicWebSocketHandler,dict(node=self))])
		self.port_list   = {}
		self.laptop_ip   = TUN_IP
		self.sniffer     = None
		self.our_ip		 = get_ip('eth0')
		self.saved  	 = 0 

	def stop(self):
		if self.sniffer:
			self.sniffer.stopSniffing()
			self.sniffer.join()

	def forward(self, msg):
		""" For the websocket to call when it gets a packet from laptop """
		packet = IP(msg)
		if not packet.haslayer(TCP):	
			print 'Packet does not contain a TCP layer. Discaring...'
			return
				
		self.remember_packet(packet)
		packet.src = self.our_ip
		packet = reset_checksum(packet)
		send(packet)

	def listen(self):
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
			
	""" After SniffingThread gets a packet off the wire, it sends it back to node to be checked and handled """
	def handle_sniffed(self, pkt):
		if self.check_remembered(pkt):
			pkt.getlayer(IP).dst = TUN_IP
			pkt = reset_checksum(pkt)
			self.ws.send(str(pkt[IP]))	

	""" Our way to keep track of which packets are worth filtering when sniffing is to have a port_list:
			we keep list of ports of sent packets as tuple (sport, dport).
			When we get a new packet from client's tun, we save its port in list 
				so that when its response comes back we can put back the correct ip to return to client
		Returns modified port_list and packet
	"""
	def remember_packet(self, new_packet):
		#if (new_packet.sport not in port_list): --should we avoid storing more than once?
		try:
			self.port_list[(new_packet.sport, new_packet.dport)] += 1
		except KeyError:
			self.port_list[(new_packet.sport, new_packet.dport)] = 1

		return new_packet
	
	""" Returns True if packet's port pair is from client-tun, False otherwise.  
		Also modifies port_list by taking out pair.  """
	def check_remembered(self, packet):
		if not packet.haslayer(TCP):
			return False
		list = self.port_list
		if (packet.dport, packet.sport) in list:
			self.port_list[(packet.dport, packet.sport)] -= 1
			if self.port_list[(packet.dport, packet.sport)] == 0:
				del self.port_list[(packet.dport, packet.sport)]
			return True

		else:
			return False


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
