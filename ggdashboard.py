#!/usr/bin/env python2.7

from __future__ import print_function

try:
	import sys
except ImportError:
	print("Module 'sys' required... please install")
	quit()

try:
	import logging as log
except ImportError:
	print("Module 'logging' required... please install")
	sys.exit(1)

#
# Arguement parsing
#

try:
	import argparse
except ImportError:
	print("Module 'argparse' required... please install")
	sys.exit(1)

p = argparse.ArgumentParser(description='GoGrid API Dashboard', prog='ggdashboard')

# OPTIONAL: --version
p.add_argument(
	'--version',
	action   = 'version',
	version  = '%(prog)s 0.1',
	help     = 'Display Version')

# OPTIONAL: -v
p.add_argument(
	'-v', '--verbose',
	required = False,
	action   = 'store_true',
	help     = 'Increase logging verbosity')

# OPTIONAL: -e {prod}
p.add_argument(
	'-e',
	required = False,
	action   = 'store',
	dest     = 'env',
	help     = 'Environment',
	choices  = ['prod'],
	default  = 'prod')

# OPTIONAL: -k API_KEY
p.add_argument(
	'-k',
	required = False,
	action   = 'store',
	dest     = 'api_key',
	help     = 'GoGrid API Key',
	default  = None)

# REQUIRED: -s API_KEY_SECRET
p.add_argument(
	'-s',
	required = False,
	action   = 'store',
	dest     = 'key_secret',
	help     = 'GoGrid API Key Secret',
	default  = None)

args = p.parse_args()
args.api_version = 1.9
args.api_format  = 'json'

if args.verbose:
	log.basicConfig(format="%(levelname)-6s: %(message)s", level=log.DEBUG)
else:
	log.basicConfig(format="%(levelname)-6s: %(message)s")

log.info('Imported : print_function')
log.info('Imported : sys')
log.info('Imported : logging')
log.info('Imported : argparse')
log.info('---------: Command line arguements parsed')
log.info('---------: Logging level set')

try:
	import os
except ImportError:
	log.error("Module 'os' required... please install")
	sys.exit(1)
finally:
	log.info('Importing: os')

try:
	import getpass
except ImportError:
	log.error("Module 'getpass' required... please install")
	sys.exit(1)
finally:
	log.info('Importing: getpass')

try:
	import curses
except ImportError:
	log.error("Module 'curses' required... please install")
	if os.name == 'nt':
		log.error("Windows 'curses' can be acquired from: http://www.lfd.uci.edu/~gohlke/pythonlibs/#curses")

	sys.exit(1)
finally:
	log.info('Importing: curses')

try:
	import json
except ImportError:
	log.error("Module 'json' required... please install")
	sys.exit(1)
finally:
	log.info('Importing: json')

try:
	import termios, fcntl
except ImportError:
	import msvcrt
else:
	if os.name == 'posix':
		log.error("Could not load 'termios' and 'fcntl'... please install")
	else:
		log.error("Could not load 'msvcrt'... please install")

	sys.exit(1)
finally:
	log.info("---------: os.name: %s" % os.name)
	if os.name == 'posix':
		log.info('Importing: termios, fcntl')
	else:
		log.info('Importing: msvcrt')

try:
	import GoGridPyLib
except ImportError:
	log.error("Module 'GoGridPyLib' required... please install")
	sys.exit(1)
finally:
	log.info('Importing: GoGridPyLib')

#
# Functions
#

def getAPIKey(args):
	log.info('Function Enter: getAPIKey')
	if args.verbose:
		log.info('Get from input: args.api_key')
		args.api_key = raw_input("%-6s: %s" % ('INFO','Key   : '))
	else:
		args.api_key = raw_input("%-6s:" % 'Key')
	log.info('Function Exit : getAPIKey')

def getAPISecret(args):
	log.info('Function Enter: getAPISecret')
	if args.verbose:
		args.key_secret = getpass.getpass("%-6s: %s" % ('INFO','Passwd: '))
	else:
		args.key_secret = getpass.getpass("%-6s:" % 'Passwd')
	log.info('Function Exit : getAPISecret')

def getENV(q):
	return {
	'prod' : 'https://api.gogrid.com/api',
	}.get(q,None)

def w_keypress():
	"""Waits for a single keypress on stdin.

	This is a silly function to call if you need to do it a lot because it has
	to store stdin's current setup, setup stdin for reading single keystrokes
	then read the single keystroke then revert stdin back after reading the
	keystroke.

	Returns the character of the key that was pressed (zero on
	KeyboardInterrupt which can happen when a signal gets handled)
	"""

	log.info('Function Enter: w_keypress()')
	if os.name == 'posix':
		log.info('Saving old state')
		fd = sys.stdin.fileno()
		flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
		attrs_save = termios.tcgetattr(fd)
		attrs = list(attrs_save)
		attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK 
			| termios.ISTRIP | termios.INLCR | termios. IGNCR 
			| termios.ICRNL | termios.IXON )
		attrs[1] &= ~termios.OPOST
		attrs[2] &= ~(termios.CSIZE | termios. PARENB)
		attrs[2] |= termios.CS8
		attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON 
			| termios.ISIG | termios.IEXTEN)
		termios.tcsetattr(fd, termios.TCSANOW, attrs)
		fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)

		log.info('read a single keystroke')

		try:
			ret = sys.stdin.read(1)
		except KeyboardInterrupt:
			ret = 0
		finally:
			log.info('restore old state')
			termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
			fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)

	else:
		log.info('read a single keystroke')
		try:
			ret = msvcrt.getch()
		except KeyboardInterrupt:
			ret = 0

	log.info("w_keypress() capture: '%s'" % str(ret))
	#log.info("w_keypress() return : '%s'" % str(ret.lower()))
	#return str(ret.lower())
	log.info('Function Exit : w_keypress()')
	return str(ret)

#
# Main
#

if __name__ == "__main__":
	log.info('Function Enter: __main__')

	if args.api_key == None:
		getAPIKey(args)

	if args.key_secret == None:
		getAPISecret(args)

	log.info('Creating client instance from GoGridPyLib')
	log.info('--')
	log.info("api_server : %s" % getENV(args.env))
	log.info("api_key    : %s" % str(args.api_key))
	log.info('key_secret : [REDACTED]')
	#log.info("key_secret : %s" % str(args.key_secret))
	log.info("api_format : %s" % args.api_format)
	log.info("api_version: %s" % str(args.api_version))
	log.info("ssl_verify : %s" % True)
	log.info('--')

	g = GoGridPyLib.client(
		api_server = getENV(args.env),
		api_key    = args.api_key,
		key_secret = args.key_secret,
		api_format = args.api_format,
		api_version= args.api_version,
		ssl_verify = True)

	log.info('Deleting variable args.key_secret for security reasons')
	del args.key_secret

	log.info('Creating main dictionary: ggassets')
	ggassets = {}

	log.info("Calling g.gridjoblist({'num_items': 2, 'page': 0, 'startdate': '2015-07-01', 'job.objecttype': [1,7]})")
	#r = g.commonlookuplist({'lookup': 'datacenter'})
	r = g.gridjoblist({'num_items': 2, 'page': 0, 'startdate': '2015-07-01', 'job.objecttype': [1,7]})

	log.info('--')
	log.info(r)
	log.info("API HTTP return code %d, %s" % (r['code'],r['cmsg']))
	log.info('--')

	print('')
	log.info('Function Exit : __main__')
	sys.exit(0)
