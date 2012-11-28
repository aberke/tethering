#! /usr/bin/python

import os
import socket
import struct
from fcntl import ioctl

IOCSIFADDR = 35094 # magic number 

""" open the tun device for both reading/writing,
    returns a file descriptor (int) """
tun = os.open('/dev/tun0', os.O_RDONLY)


""" set up for the ioctl """
addrstr = '10.0.0.1'
addr    = socket.inet_pton(socket.AF_INET, addrstr)

ifname = 'tun0'
ifr_name = ifname + '\0'*(32-len(ifname))
ifr_name_packed = ifr_name.encode('utf-8')

ifreq = struct.pack('sL', ifr_name_packed , addr)

""" ifconfig it """
ioctl(tun, IOCSIFADDR, ifreq)


print('falling asleep...')
time.sleep(15)
print('woke up!')



""" this tries to read 100 bytes from
    the tun device """
c = os.read(tun,100) 
