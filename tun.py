#! /usr/bin/python

from ioctl_compat.ioctl_numbers import IOC_IN, IOC_OUT

#sudo /sbin/ifconfig en1 inet 169.254.134.89 netmask 255.255.0.0 alias

#import os
#import socket
#import struct
#from fcntl import ioctl
#
#SIOCGIFADDR = 0x8915 # magic number 
#
##""" open the tun device for both reading/writing,
##    returns a file descriptor (int) """
##tun = os.open('/dev/tun0', os.O_RDONLY)
##
##
##""" set up for the ioctl """
##addrstr = '10.0.0.1'
##addr    = socket.inet_pton(socket.AF_INET, addrstr)
##
##ifname = 'tun0'
##ifr_name = ifname + '\0'*(32-len(ifname))
##ifr_name_packed = ifr_name.encode('utf-8')
##
##ifreq = struct.pack('sL', ifr_name_packed , addr)
##
#""" ifconfig it """
#
#s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
#print(ioctl(s.fileno(), SIOCGIFADDR, struct.pack('256s', bytearray('lo0', 'utf-8'))))
#
#
#""" this tries to read 100 bytes from
#    the tun device """
##c = os.read(tun,100) 
