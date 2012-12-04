#!/usr/bin/python

"""
Author: Neil Fulwiler, Alex Berke
Date  : 11.26.2012
Usage : Static file server to serve web app files to the tethering phone
"""

import tornado.ioloop
import tornado.web
import sys
import os

port = 8080

filepath = "webapp/webapp.html"

# sudo /sbin/ifconfig en1 inet 169.254.134.89 netmask 255.255.0.0 alias

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

#^^^^^^^^^
# handlers
#
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
	settings = {"static_path": os.path.join(os.path.dirname(__file__), 'webapp')} 

	try:
		application = tornado.web.Application([
			(r"/(webapp\.\w+)", tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
    	], settings)
		application.listen(port)
	except Exception as e:
		print e.args
		sys.exit(0)

	try:
		ioloop.add_handler(sys.stdin.fileno(), stdinHandler, ioloop.READ)
		print 'running...'
		ioloop.start()
	except:
		print("Error: could not start ioloop")
		
		
