"""
Author: Neil Fulwiler, Alex Berke
Date  : 12.6.2012
Usage : A basic websocket handler that we will use to pass messages
		to the node
"""

import tornado.websocket as websocket

class BasicWebSocketHandler(websocket.WebSocketHandler):
	""" If you are using an iPhone as your mobile device, with Safari as the web
	browser, you will need to override WebSocketHandler.allow_draft76() to return True. Other-
	wise, your websocket requests will never be accepted by the server. """	
	def __init__(self,application,request,**kwargs):
		websocket.WebSocketHandler.__init__(self,application,request)
		self.node    = kwargs['node'] 
		print 'initailized'

	def allow_draft76(self):		
		return True
		
	def open(self):
		self.node.ws = self
		print 'connection assigned'

	def on_message(self, message):
		decoded = message.decode('base64')
		#print 'got message:', message, 'decoded to:', decoded 
		self.node.forward(decoded)

	def send(self, msg):
		self.write_message(msg.encode('base64'))

	def on_close(self):
		print 'websocket closed'	

