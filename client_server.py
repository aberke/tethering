#! /usr/bin/python

"""
Author: Neil Fulwiler, Alex Berke
Date  : 11.30.2012
Usage : Opens tun device and creates stream between tun and websocket
"""

#from ioctl_compat.ioctl_numbers import IOC_IN, IOC_OUT
import tornado.web
import tornado.websocket as websocket
import tornado.ioloop
from fcntl import ioctl
import struct
import sys
import os
import subprocess
import threading


"""Before we can run the websocket server which will bind to that address, we must assign that IP
address to the Wi device of the laptop. To do so, run the following command, substituting en1
with your Wifi device name.
sudo /sbin/ifconfig en1 inet 169.254.134.89 netmask 255.255.0.0 alias 
ALEX: The issue for me is that for me to make this call on my computer I need to provide my credentials, kinda sketch 
		so I'm doing it before I run this in my terminal """
# wifi_device = 'en1' # <-- that's what works on my computer (Alex)
# try:
# 	#subprocess.check_call('sudo /sbin/ifconfig en1 inet 169.254.134.89 netmask 255.255.0.0 alias', shell=True)
# 	subprocess.check_call('sudo /sbin/ifconfig '+wifi_device+' inet 169.254.134.89 netmask 255.255.0.0 alias')
# except subprocess.CalledProcessError:
# 	print('Error: '+subprocess.CalledProcessError.returncode);
	


# Calls like these should be helpful for debugging I think
# subprocess.check_output("exit 1", shell=True)

# the port to use
port = 6354 #4

# Make the application instance and tun instance global so that we can use it inside the threading run function
global application
global tunfd
global running

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# commands

def startTun():
	try: 
		initializeTun()
		tun_thread = tunThread()
		tun_thread.start()
		print 'running tun device...'
	except Exception, err:
		raise Exception('ERROR in initialize start tun: %s\n' % str(err))

def quit():
	ioloop.stop()
def stars():
	print('**********************************************************')
def write():
	global application
	if application.ws:
		application.ws.write_message('********************************')
def encodedWrite():
	global application
	if application.ws:
		msg = 'THIS IS A MESSAGE I AM ENCODING AND DECODING 1234'
		application.ws.write_message(msg.encode('base64'))

commands={\
'startTun':startTun,
'q':quit,
'quit':quit,
's':stars,
'write':write,
'ewrite':encodedWrite,
}

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# tun 

def initializeTun():
	# path to the tun device, and open
	# the file descriptor
	global tunfd
	tunpath = '/dev/tun0'  
	tunfd   = os.open(tunpath, os.O_RDWR) #	
	"""
	Once you have your TUN/TAP device set up, there's one final step. You need to instruct your
	laptop OS to take all outgoing network requests and send them into the TUN device instead of
	using the standard networking interface (i.e. eth0). To do so, you need to assign your TUN device
	a known IP address:
	sudo ifconfig tun0 10.0.0.1 10.0.0.1 netmask 255.255.255.0 up
	Then, modify the OS's IP routing table to delete the current default route, and route all network
	traffic through the tunnel:
	sudo route delete default; sudo route add default 10.0.0.1
	"""	
	try: 
		subprocess.check_call('sudo ifconfig tun0 10.0.0.1 10.0.0.1 netmask 255.255.255.0 up', shell=True)
		subprocess.check_call('sudo route delete default', shell=True)
		subprocess.check_call('sudo route add default 10.0.0.1', shell=True)
	except Exception, err:
		raise Exception('ERROR in initialize tun method: %s\n' % str(err))

class tunThread(threading.Thread):
	def run(self):
		global tunfd
		global running
		global application
		running = True
		print 'about to start tun thread while loop'
		while(running):
			message = os.read(tunfd, 1500) #I put 1500 because that's the ethernet IP packet size -- but should it be bigger?? I don't want to truncate the packet
			encodedmsg = message.encode('base64')
			print('message read from tunfd: '+message)
			print('encoded message read from tunfd: '+encodedmsg)
			if application.ws:
				application.ws.write_message(encodedmsg)
				print('******************************** wrote message to application ********************************')
					

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# handlers

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
	def allow_draft76(self):		
		return True
        
	def open(self):
		global application
		application.ws = self
		print 'Score. Opened'

	def on_message(self, message):
		global tunfd
		print('got message: ' + message)
		# os.write(tunfd, message.decode('base64'))
		
	def on_close(self):
		print 'websocket closed'	

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# int main(int argc, char** argv)
#

if __name__=='__main__':
	# need to use these global variables
	global tunfd
	tunfd = None
	global running
	global application
	try:
		# the event loop
		ioloop = tornado.ioloop.IOLoop.instance()
		ioloop.add_handler(sys.stdin.fileno(), stdinHandler, ioloop.READ)
		# initialize application and listen
		application = tornado.web.Application([
			(r'/websocket', BasicWebSocket),
		])
		application.ws = None
		subprocess.check_call('sudo /sbin/ifconfig en1 inet 169.254.134.89 netmask 255.255.0.0 alias', shell=True)
		application.listen(port)
		print 'running...'
	except Exception, err:
		raise Exception('Error: %s\n' % str(err))
	try:
		ioloop.start()
	except Exception, err:
		raise Exception('Error: %s\n' % str(err))
	finally:
		running = False #this should end the tunThread, right?
		if tunfd:
			os.close(tunfd)

