#!/usr/bin/python2.7

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
import sys
import os

# the port to use
port = 6354

# path to the tun device, and open
# the file descriptor
tunpath = '/dev/tun0'  
tunfd   = os.open(tunpath, os.O_RDWR) #<-- I get permission denied

# the event loop
ioloop = tornado.ioloop.IOLoop.instance()

#^^^^^^^^^^ 
# commands
#

def quit():
	ioloop.stop()
def stars():
	print('**********************************************************')

commands={\
'q':quit,
'quit':quit,
's':stars,
}

#^^^^^^^^^^^^^^^^^^
# initialize tun 
#

def initializeTun():
	""" here we should be using ioctl() to ifconfig 
		the tun device and make it ready for reading/writing,
		don't ask me how to do that """
	ioctl(tunfd, SOMETHING, ELSE)

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
	def open(self):
		print 'Score. Opened'

	def on_message(self, message):
		print('got message: ' + message)
		
	def on_close(self):
		print 'websocket closed'	

application = tornado.web.Application([
	(r'/websocket', BasicWebSocket),
])

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# int main(int argc, char** argv)
#

if __name__=='__main__':
	try:
		application.listen(port)
		ioloop.add_handler(sys.stdin.fileno(), stdinHandler, ioloop.READ)
		ioloop.start()
	finally:
		os.close(tunfd)
