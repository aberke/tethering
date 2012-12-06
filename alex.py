#!/usr/bin/env python

#alex plays with scapy after getting packets from tun

import logging
logging.getLogger("scapy").setLevel(1)
import subprocess
from scapy.all import *
import socket
import fcntl
import struct

TUN_IP = '10.0.0.1' # we strip this off packet and replace source with our own source, but need to put back on packet upon return

"""For TCP, disable the kernel's response with:"""
subprocess.check_call('sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP', shell = True)
""" to set it back: """
#subprocess.check_call('sudo iptables -D OUTPUT -p tcp --tcp-flags RST RST -j DROP', shell = True)

""" sample use: get_ip_address('eth0') returns '38.113.228.130' """
def get_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

""" Our way to keep track of which packets are worth filtering when sniffing is to have a port_list:
		we keep list of ports of sent packets as tuple (sport, dport).
		When we get a new packet from client's tun, we save its port in list 
			so that when its response comes back we can put back the correct ip to return to client
	Returns modified port_list and packet
"""
def remember_packet(port_list, new_packet):
	#if (new_packet.sport not in port_list): --should we avoid storing more than once?
	port_list.append((new_packet.sport, new_packet.dport))
	return port_list, new_packet

""" Returns True if packet's port pair is from client-tun, False otherwise.  
	Also modifies port_list by taking out pair.  """
def check_remembered(port_list, packet):
	if ((packet.dport, packet.sport) in port_list):
		port_list.remove((packet.dport, packet.sport))
		return True
	else:
		return False

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
	return packet	

#def modify_send_packet_from_file(file_name):
def m(file_name, port_list):
	if(not port_list):
		port_list = []
	packet = msg_to_packet(file_name)
	remember_packet(port_list, packet)
	print 'original ip packet:'
	print('packet.src: '+str(packet.src))
	print('packet.dst: '+str(packet.dst))
	our_ip = get_ip('eth0')
	print('new packet src: '+our_ip)
	packet.src = our_ip
	# need to reset checksum
	packet = reset_checksum(packet)
	
	return packet, port_list
	
	