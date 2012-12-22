# Collection of functions for ofProjectManager

import logging
import os
import sys
import subprocess

logger = logging.getLogger(__name__)

def validate_git_repo(strict=True):
	"""Validate if current directory is in a git repo."""
	
	logger.debug('Checking if in a git repository?')
	# python3.3 offers subpocess.DEVNULL for output redirection
	if (subprocess.call(['git','rev-parse']) == 0) and (subprocess.call('git clean -xnd `pwd` | grep "Would remove \./" > /dev/null',shell=True) == 1):
	# we are in a git repository, but not in an ignored directory inside a git repo (i.e. in OF/addons)
		logger.debug('Yes, this is in a git repository.')
		if subprocess.call(['git','diff','--quiet','HEAD']) != 0:
			logger.error('Repository has uncommitted changes, commit those before continuing!')
			return 1
		else:
			logger.debug('Repository clean')
			return 0
	else:
		if strict is True:
			logger.error(os.getcwd() + ' is not in a git repository!')
			return 1
		else:
			logger.warning(os.getcwd() + ' is not in a git repository!')
			return 2

def record(args):
	logger.debug('In subcommand record.')
	os.chdir(args.project)
	
	# parse addons.make into a list of addons
	# TODO: use with here
	addons_make = open('addons.make','r')
	#TODO: use dict from beginning
	addons_list=[]
	for l in addons_make.readlines():
		addons_list.append(l.rstrip())
	if len(addons_list) is 0:
		logger.info('No addons found.')
	addons_make.close()
	
	# search config.make for OF location
	# TODO: use with here
	config_make = open('config.make','r')
	OF_path=''
	for l in config_make.readlines():
		if 'OF_ROOT =' in l:
			OF_path=l.split('=',1)[-1].strip()
			break
	if len(OF_path) == 0:
		logger.error('Did not find OF location in config.make in ' + os.getcwd())
		config_make.close()
		os.chdir(args.project)
		sys.exit('Aborting.')
	config_make.close()
	
	logger.info('Processing OF')
	os.chdir(OF_path)
	if validate_git_repo() !=0:
		sys.exit('Aborting.')
		
	logger.debug('Recording commit SHA')
	OF_commit_SHA=subprocess.check_output(['git','rev-parse','HEAD']).strip()
	logger.debug('OF commit SHA: '+ OF_commit_SHA)
	
	logger.info('Processing addons')
	addons_path=os.path.join(os.getcwd(),'addons')
	os.chdir(addons_path)
	# get list of official addons
	official_addons=[]
	with open('.gitignore','r') as g:
		for line in g:
			if line.startswith('!ofx'):
				official_addons.append(line[1:].strip())
	# prune official addons (which are in the OF repo already
	# not very efficient (better with sets), but irrelevant for the small lists we expect
	addons_list = [x for x in addons_list if x not in official_addons]
	addons_dict = dict.fromkeys(addons_list)
	for k,v in addons_dict.iteritems():
		logger.info('Processing addon ' + k)
		os.chdir(os.path.join(addons_path,k))
		ret= validate_git_repo(strict=False)
		if ret == 0:
			addons_dict[k] = subprocess.check_output(['git','rev-parse','HEAD']).strip()
		elif ret == 2:
			addons_dict[k] = 'no-git'
		else:
			sys.exit('Aborting.')
	logger.debug(addons_dict)
	
	#TODO: go to project directory, put info into file. 
	#TODO: use JSON

	return 0
	


    
def checkout(args):
	logger.debug('In subcommand checkout.')
	logger.error('This is not yet implemented.')
	sys.exit('Aborting')
	return 0



def collect(args):
	logger.debug('In subcommand collect.')
	logger.error('This is not yet implemented.')
	sys.exit('Aborting')
	return 0
