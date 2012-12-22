# Collection of functions for ofProjectManager

import logging
import os
import sys
import subprocess
import json
import errno
from datetime import datetime

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
			logger.error('Not in a git repository: ' + os.getcwd())
			return 1
		else:
			logger.warning('Not in a git repository: ' + os.getcwd())
			return 2

def record(args):
	logger.debug('In subcommand record.')
	os.chdir(args.project)
	projectpath=os.getcwd()
	
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
		sys.exit('Aborting.')
	config_make.close()
	
	logger.info('Processing OF')
	os.chdir(OF_path)
	core_dict={'path': OF_path}
	if validate_git_repo() !=0:
		sys.exit('Aborting.')
		
	logger.debug('Recording commit SHA')
	core_dict['sha']=subprocess.check_output(['git','rev-parse','HEAD']).strip()
	logger.debug('OF commit SHA: '+ core_dict['sha'])
	
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
	addons_list = [{'name': x} for x in addons_list if x not in official_addons]
#	addons_dict = dict.fromkeys(addons_list)
	for addon in addons_list:
		logger.info('Processing addon ' + addon['name'])
		try:
			os.chdir(os.path.join(addons_path,addon['name']))
		except Exception as e:
			if e.errno == errno.ENOENT:
				logger.error(addon['name'] + ' does not exist at ' + addons_path + '. Aborting.')
				sys.exit('Aborting')
			else:
				logger.error('error: ' + str(e))
			
		ret= validate_git_repo(strict=False)
		if ret == 0:
			addon['sha'] = subprocess.check_output(['git','rev-parse','HEAD']).strip()
		elif ret == 2:
			addon['sha'] = 'non-git'
		else:
			sys.exit('Aborting.')
#	logger.debug(addons_list)
	
	logger.info('Storing metadata')
	filename='metadata.json'
	os.chdir(projectpath)
	
	# Open/initialise metadata file
	try:
		with open(filename,'r') as metafile:
			json_object = json.load(metafile)
			logger.info('loaded data from ' + filename)
			logger.debug(json_object)
			# update with data
	except IOError as e:
		if e.errno == errno.ENOENT:
			logger.info(filename + ' does not exist. Creating..')
			open(filename,'w').close()
			# create new skeleton json_object
			json_object=json.loads('{ "snapshots": [] }')
		else:
			logger.error('Could not open file: ' + e)
			sys.exit('Aborting')
	
	# Store/update metadata
	# check if snapshot entry already exists
	for entry in json_object['snapshots']:
		if entry['name'] == args.name:
			if (args.update is False) and (args.name is not 'latest'):
				logger.error(args.name + ': entry with the same name already exists. Use -u option to overwrite.')
				sys.exit('Aborting')
			json_object['snapshots'].remove(entry)
	
	# write updated entry
	temp= {'name': args.name, 'date': datetime.now().isoformat(), 'core': core_dict, 'addons': addons_list}
	json_object['snapshots'].append(temp)
	
	logger.info('Writing updated data to ' + filename)
	with open(filename,'w') as metafile:
		json.dump(json_object, metafile,indent=1,sort_keys=True)

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
