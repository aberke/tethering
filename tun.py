#! /usr/bin/python

import os

# open the tun device for both reading/writing,
# returns a file descriptor (int)
tun = os.open('/dev/tun0', os.O_RDONLY)

# this tries to read 100 bytes from
# the tun device
c = os.read(tun,100) 
