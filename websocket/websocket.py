import tornado.ioloop
import functools
import socket

""" most of the below is from a simple tutorial at 
	www.tornadoweb.org/documentation/ioloop.html """


class WebSocket(object):
	def __init__(self, ip, port):
		""" intiialize the socket """
		addr = (ip, port)
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)
		self.sock.bind(addr)

	def handle_connection(self, connection, address):
		print 'got connection! Now what?'
		return

	def connection_ready(self, fd, events):
		while True:
			try:
				connection, address = sock.accept()
			except socket.error, e:
				if e.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
					raise
				return
			
			connection.setblocking(0)
			handle_connection(connection, address)

	def start(self):
		self.loop = tornado.ioloop.IOLoop.instance()
		self.loop.add_handler(self.sock.fileno(), self.connection_ready, self.loop.READ)
		self.loop.start()



