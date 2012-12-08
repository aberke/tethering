import sys
sys.path.append('/home/ubuntu/lib') # sorry 

import os
import node
import tornado.ioloop
import webPage


def error(msg):
	""" error

	for now simply prints the error message 
	"""
	print 'Error:', msg

def quit():
	"""	quit:
	
	quit's the program 
	"""
	sys.exit(0)

def help():
	""" help:	
		
	print out the commands 
	"""
	functions={}
	for f in commands:
		try:
			functions[commands[f]].append(f)
		except KeyError:
			functions[commands[f]] = [f]

	for f in functions:
		cmds = ''
		for fcmd in functions[f]:
			cmds+=fcmd+','	
		cmds=cmds.strip(',')
		print cmds
		print f.__doc__

def stars():
	""" prints some stars """
	print '*********************************'

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# node 
def listen():
	""" listen:
		
	starts the node listening """
	getInstance(node.Node).listen()

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# web 
def web():
	""" web:
		
	starts the static file server """ 
	webpage = getInstance(webPage.WebPage)
	webpage.listen()

#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# commander
class Commander(object):
	def __init__(self):
		self.todo = []	

	def add(self, toadd):
		self.todo.append(toadd)
	
	def teardown(self):
		for todo in self.todo:
			todo()

def getInstance(singletonClass,*args):
	""" singleton factory """
	if singletonClass not in getInstance.singletons:
		getInstance.singletons[singletonClass]=apply(singletonClass,args)
	return getInstance.singletons[singletonClass]
getInstance.singletons={}
			
commands=\
{	
	'q':quit,
	'quit':quit,
	'h':help,
	'help':help,
	'listen':listen,
	's':stars,
	'stars':stars,
	'web':web
}

def stdinHandler(fd, events):
	""" handle reading from stdin and dispatching
		commands
	"""
	buff = sys.stdin.readline().strip()
	cmdline =buff.split(' ')
	cmd     =cmdline[0]

	try:
		retval = apply(commands[cmd], cmdline[1:])	
		if retval != None:
			print retval
	except TypeError as te:
		error(te.args[0])
	except KeyError:
		print 'Unrecognized command:', cmd 
	except Exception as e:
		print 'Exception caught:', e.args[0]

"""
main
	runs the main program 
"""
def main():
	commander = getInstance(Commander)	

	""" tell the commander to clean up the node """
	nodeinst  = getInstance(node.Node)
	commander.add(nodeinst.stop)

	""" add the stdin handler, and tell the commander to clean up the ioloop """
	ioloop    = tornado.ioloop.IOLoop.instance()
	getInstance.singletons[tornado.ioloop.IOLoop] = ioloop
	ioloop.add_handler(sys.stdin.fileno(), stdinHandler, ioloop.READ)
	commander.add(ioloop.stop)

	""" now serve the web-page, start listening """
	web()
	listen()

	""" start it up! """
	ioloop.start()

if __name__=='__main__':
	try:
		main()
	except SystemExit:
		getInstance(Commander).teardown()
	
