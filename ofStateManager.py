#!/usr/bin/python
import logging
import argparse
import sys
from os import getcwd
import manager_functions as mgr

logger = logging.getLogger(__name__)

#*************************************
# command line argument parser
parser = argparse.ArgumentParser(description='Record and restore the state of your openFrameworks projects and archive their files.')
#Parent parser contains common options
parent_parser = argparse.ArgumentParser(add_help=False)
parent_parser.add_argument('-p', '--project', default=getcwd(), help='Path to the desired project directory, defaults to the current directory if this option is not given')
parent_parser.add_argument('-n', '--name', default='latest', help='Name of the desired state, defaults to "latest" if this option is not given')
parent_parser.add_argument('-v', '--verbose', action='store_true', help='Switch on debug logging.')

subparsers = parser.add_subparsers(help='Available commands')
record_parser = subparsers.add_parser('record', help='Record the state of all relevant components', parents=[parent_parser])
record_parser.add_argument('-u', '--update', action='store_true', help='If name already exists, overwrite existing entry')
record_parser.set_defaults(func=mgr.record)

checkout_parser = subparsers.add_parser('checkout', help='Check out the complete named or latest state of your project and OF', parents=[parent_parser])
checkout_parser.set_defaults(func=mgr.checkout)

archive_parser = subparsers.add_parser('archive', help='Archive all relevant components for the named or latest state', parents=[parent_parser])
# target actually doesn't make much sense - should go into project directory anyway
# archive_parser.add_argument('-t', '--target', default=getcwd(), help='Target path where to place the archive directory, defaults to current directory')
archive_parser.add_argument('-f', '--force', action='store_true', help='When no name is given, ignore warning, check out "latest"')
archive_parser.set_defaults(func=mgr.archive)

#args=parser.parse_args()
args=parser.parse_args('record -v  '.split()) #pass '-xyzZ'.split() for debugging

#Verify option/argument validity
#TODO: verification routines

# Initialisation
if args.verbose is True:
	logging.basicConfig(level=logging.DEBUG)
else:
	logging.basicConfig(level=logging.INFO) # DEBUG/INFO/WARNING/ERROR/CRITICAL

logger.debug(args)

#Main function
logger.info('Start processing.')
if args.func(args) is not 0:
	logger.error('An error occurred during splicing!')
logger.info('Finished processing!')

#Cleanup
logging.shutdown()

