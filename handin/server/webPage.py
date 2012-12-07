"""
Author: Neil Fulwiler, Alex Berke
Date  : 11.26.2012
Usage : Static file server to serve web app files to the tethering phone
"""

import tornado.web
import os

filepath = "webapp/webapp.html"
port = 8080

class WebPage(object):	
	def __init__(self):
		settings = {"static_path": os.path.join(os.path.dirname(__file__), 'webapp')} 
		try:
			self.application = tornado.web.Application([
				(r"/(\w+\.\w+)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
	    	], settings)
		except Exception, e:
			print e.args

	def listen(self):
		self.application.listen(port)		
	

