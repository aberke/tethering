"""
Trying to replicate Mac OSX macros defined in <sys/ioccom.h>
"""

#define	IOC_IN		(__uint32_t)0x80000000
#define IOC_OUT		(__uint32_t)0x40000000
#define IOC_INOUT   (IOC_IN|IOC_OUT)

#define _IOWR(g,n,t) _IOC(IOC_INOUT,	(g), (n), sizeof(t))
#define	_IOC(inout,group,num,len) (inout | ((len & IOCPARM_MASK) << 16) | ((group) << 8) | (num))
#define	_IO(g,n)	_IOC(IOC_VOID,	(g), (n), 0)
#define	_IOR(g,n,t)	_IOC(IOC_OUT,	(g), (n), sizeof(t))
#define	_IOW(g,n,t)	_IOC(IOC_IN,	(g), (n), sizeof(t))
#define	_IOWR(g,n,t)	_IOC(IOC_INOUT,	(g), (n), sizeof(t))

import subprocess
import re

compat_dir  = 'ioctl_compat'
compat_exe_name  = 'ioctl_compat'
compat_file_name = 'compat.numbers'

compat_exe  = compat_dir+'/'+compat_exe_name
compat_file = compat_dir+'/'+compat_file_name

""" run the ioctl_compat file to get the required IOC_IN/IOC_OUT numbers """
try:
	subprocess.check_output(
		[compat_exe+' '+compat_file],
		stderr=subprocess.STDOUT,
		shell=True)
except subprocess.CalledProcessError as e:
	raise Exception('Error running compatibility executable: ' + str(e.output))

""" now read the file that the above process output in order to extract the
	system dependent numbers """

# wow I got carred away with that one-liner
IOC_IN  = [int(y.group(1)) for y in [re.match('IOC_IN:(\d*)',x) for x in open(compat_file)] if y][0]
IOC_OUT = [int(y.group(1)) for y in [re.match('IOC_IN:(\d*)',x) for x in open(compat_file)] if y][0]

IOC_INOUT = IOC_IN|IOC_OUT

