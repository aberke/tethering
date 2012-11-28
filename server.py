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
import sys

port = 6354

ioloop = tornado.ioloop.IOLoop.instance()

#^^^^^^^^^^ 
# commands
#

def quit():
	ioloop.stop()

commands={\
'q':quit,
'quit':quit,
}

#^^^^^^^^^
# handlers

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

#^^^^^^^^^^^
# int main()

if __name__=='__main__':
	application.listen(port)
	ioloop.add_handler(sys.stdin.fileno(), stdinHandler, ioloop.READ)
	ioloop.start()
