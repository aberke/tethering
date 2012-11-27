#!/usr/bin/python

""" ew! sorry about that. Please feel free to rename
	anything and everything you wish """
import websocket.websocket as websocket

IP   = '169.254.134.89'
PORT = 6354

if __name__ == '__main__':
	webs = websocket.WebSocket(IP, PORT)
	webs.start()
