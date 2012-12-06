#!/usr/bin/python

"""
Author: Neil Fulwiler, Alex Berke
Date  : 11.26.2012
Usage : Just a simple server using the tornado API
		in order to test out the js websockets
		that will be used in the webapp
"""

import tornado.web
import tornado.websocket as websocket
import tornado.ioloop
from fcntl import ioctl
import struct
import subprocess
import sys
import os

# the port to use
port =  6354 # 8081


# the event loop
ioloop = tornado.ioloop.IOLoop.instance()

# sniffingThread instance
sniffer = None

connection = None

#^^^^^^^^^^ 
# commands
#

def encodedWrite():
	global connection
	if connection:
		msg = 'THIS IS A MESSAGE I AM ENCODING AND DECODING 1234'
		connection.write_message(msg.encode('base64'))

def write():
	global connection
	if connection:
		connection.write_message('********************************')

def quit():
	ioloop.stop()
def stars():
	print('**********************************************************')

commands={\
'q':quit,
'quit':quit,
's':stars,
'write':write,
'ewrite':encodedWrite,
}


#^^^^^^^^^
# handlers
#

def stdinHandler(fd, events):
	buff = sys.stdin.readline().strip()
	try:
		commands[buff]()
	except KeyError:
		print('Command not recognized:'+buff)

class BasicWebSocket(websocket.WebSocketHandler):
	""" If you are using an iPhone as your mobile device, with Safari as the web
	browser, you will need to override WebSocketHandler.allow_draft76() to return True. Other-
	wise, your websocket requests will never be accepted by the server. """	
	def __init__(self,application, request, **kwargs):
		websocket.WebSocketHandler.__init__(self, application, request, **kwargs)

		def allow_draft76(self):
			return True
		self.allow_draft76 = allow_draft76
		
	def open(self):
		print 'Score. Opened'
		global connection
		connection = self
		print 'connection assigned'

	def on_message(self, message):
		print('got message: ' + message)
		print('message decoded: '+message.decode('base64', 'strict'))
		
	def on_close(self):
		print 'websocket closed'	

import socket
import fcntl
import struct

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# int main(int argc, char** argv)
#
if __name__=='__main__':
	try:
		application = tornado.web.Application([
			(r'/websocket', BasicWebSocket),
		])
		application.listen(port)
	except Exception, err:
		print('Error: could not initialize application and listen'+str(err))
	try:
		ioloop.add_handler(sys.stdin.fileno(), stdinHandler, ioloop.READ)
		print 'running ...'
		# our ip address that we need to assign to outgoing packet that we forward:
		our_ip = get_ip_address('eth0')
		print('our ip address of eth0 to assign to packets: '+our_ip)
		ioloop.start()
