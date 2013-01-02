# Collection of functions for ofProjectManager

import logging
import os
import sys
import subprocess
import json
import errno
from datetime import datetime

logger = logging.getLogger(__name__)

###############################################################################
def validate_git_repo(strict=True):
	"""Validate if current directory is in a git repo.
	
	Return 0 on success, 1 on error if not in a git repo, 
	2 for warning about not being in a git repo"""
	
	logger.debug('Checking if in a git repository?')
	# python3.3 offers subpocess.DEVNULL for output redirection
	if (subprocess.call(['git','rev-parse']) == 0) and (subprocess.call('git clean -xnd `pwd` | grep "Would remove \./" > /dev/null',shell=True) == 1):
	# we are in a git repository, but not in an ignored directory inside a git repo (i.e. in OF/addons/someAddon)
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

###############################################################################		
def git_archive_repo(archivename, archivepath, repopath, repo_sha):
	"""Archive a git repo snapshot in the given archive file."""
	
	try:
		with open(archivename,'r') as archivefile:
			logger.info(archivename + ' already exists. Skipping ...')
	except IOError as e:
		if e.errno == errno.ENOENT:
			os.chdir(archivepath)
			logger.info('Archiving ' + archivename)
			os.chdir(repopath)
			# git archive --format=tar.gz --output=arch.tar.gz --remote=./openFrameworks/ sha
			subprocess.call(['git','archive','--format=tar.gz','--output='+os.path.abspath(os.path.join(archivepath,archivename)),'--prefix='+os.path.basename(repopath)+os.sep,repo_sha])
			# This doesn't work with the remote option, since git repos don't allow clients access to arbitrary sha's, only named ones.
			# Solution: go to repo directory, use -o to put resulting file into right path
			# cf. http://git.661346.n2.nabble.com/Passing-commit-IDs-to-git-archive-td7359753.html
			# TODO: error catching
			os.chdir(archivepath)
		else:
			raise
			
###############################################################################
def check_for_snapshot_entry(name,json_object):
	"""Return snapshot entry if it already exists."""
	return_entry={}
	for entry in json_object['snapshots']:
		if entry['name'] == name:
			logger.info('Selecting snapshot '+ name)
			return_entry=entry
			break
	return return_entry

###############################################################################
def record(args, filename):
	"""Record a snapshot in a json file, as specified by arguments in args.
	
	Return 0 on success, 1 on failure."""
	
	logger.debug('In subcommand record.')
	os.chdir(args.project)
	projectpath=os.getcwd()
	
	# parse addons.make into a list of addons
	with open('addons.make','r') as addons_make:
		#TODO: use dict from beginning
		addons_list=[]
		for l in addons_make.readlines():
			addons_list.append(l.rstrip())
		if len(addons_list) is 0:
			logger.info('No addons found.')
	
	# search config.make for OF location
	with open('config.make','r') as config_make:
		OF_path=''
		for l in config_make.readlines():
			if 'OF_ROOT =' in l:
				OF_path=l.split('=',1)[-1].strip()
				break
		if len(OF_path) == 0:
			logger.error('Did not find OF location in config.make in ' + os.getcwd())
			return 1
	
	logger.info('Processing OF')
	os.chdir(OF_path)
	core_dict={'path': OF_path}
	if validate_git_repo() !=0:
		logger.error('OF git repo could not be validated successfully.')
		return 1
		
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
	# prune official addons (which are in the OF repo already)
	# not very efficient (better with sets), but irrelevant for the small lists we expect
	addons_list = [{'name': x} for x in addons_list if x not in official_addons]
	
	for addon in addons_list:
		logger.info('Processing addon ' + addon['name'])
		try:
			os.chdir(os.path.join(addons_path,addon['name']))
		except Exception as e:
			if e.errno == errno.ENOENT:
				logger.error(addon['name'] + ' does not exist at ' + addons_path + '. Aborting.')
				sys.exit('Aborting')
			else:
				raise
			
		ret= validate_git_repo(strict=False)
		if ret == 0:
			addon['sha'] = subprocess.check_output(['git','rev-parse','HEAD']).strip()
		elif ret == 2:
			addon['sha'] = 'non-git'
		else:
			logger.error(addon['name'] + ' git repo could not be validated successfully.')
			return 1
	
	logger.info('Storing metadata')
	os.chdir(projectpath)
	
	# Open/initialise metadata file
	try:
		with open(filename,'r') as metafile:
			json_object = json.load(metafile)
			logger.info('loaded data from ' + filename)
			logger.debug(json_object)
	except IOError as e:
		if e.errno == errno.ENOENT:
			logger.info(filename + ' does not exist. Creating..')
			open(filename,'w').close()
			# create new skeleton json_object
			json_object=json.loads('{ "snapshots": [] }')
		else:
			raise
	
	# Store/update metadata
	# check if snapshot entry already exists
	for entry in json_object['snapshots']:
		if entry['name'] == args.name:
			if (args.update is False) and (args.name is not 'latest'):
				logger.error(args.name + ': entry with the same name already exists. Use -u option to overwrite.')
				return 1
			json_object['snapshots'].remove(entry)
	
	# write updated entry
	temp= {'name': args.name, 'date': datetime.now().isoformat(), 'core': core_dict, 'addons': addons_list}
	json_object['snapshots'].append(temp)
	
	logger.info('Writing updated data to ' + filename)
	with open(filename,'w') as metafile:
		json.dump(json_object, metafile,indent=1,sort_keys=True)

	return 0

###############################################################################
def archive(args, filename):
	"""Archive a snapshot from a json file, as specified by arguments in args.
	
	Return 0 on success, 1 on failure."""
	logger.debug('In subcommand archive.')
	basedir=os.getcwd()
	os.chdir(args.project)
	projectpath=os.getcwd()	
	
	logger.debug('Opening metadata file')
	try:
		with open(filename,'r') as metafile:
			json_object = json.load(metafile)
			logger.info('loaded data from ' + filename)
			logger.debug(json_object)
			# update with data
	except IOError as e:
		if e.errno == errno.ENOENT:
			logger.info('Metadata file ' + filename + ' does not yet exist. Creating...')
			os.chdir(basedir)
			if record(args) == 0:
				os.chdir(basedir)
				return archive(args) # call archive recursively
			else:
				logger.error('Creation of snapshot ' + args.name + 'failed.')
				return 1
		else:
			raise
		
	# check if snapshot entry already exists, if not create it
	entry = check_for_snapshot_entry(args.name,json_object)
	if not entry:
		logger.info('Entry ' + args.name + ' does not exist yet. Creating...')
		os.chdir(basedir)
		if record(args,filename) == 0: # call record to create the necessary entry
			os.chdir(basedir)
			return archive(args,filename) # call archive recursively
		else:
			logger.error('Creation of snapshot ' + args.name + 'failed.')
			return 1
	#--------------------------------------------------------------------------
	else:
		# entry exists, start archiving
		# create subdirectory for archive
		archivedirectory=os.path.basename(projectpath)+'_archive'
		try:
			os.mkdir(archivedirectory)
		except OSError as e:
			if e.errno == errno.EEXIST:
				logger.debug('Directory '+archivedirectory+' already exists. Continuing.')
			else:
				logger.error('Could not create directory: ' + archivedirectory + ': ' + str(e))
				raise
		os.chdir(archivedirectory)
		
		# archive all elements
		# OF itself
		archivename=str(os.path.basename(projectpath))+'_'+entry['name']+'_OF_'+entry['core']['sha'][0:7]+'.tar.gz'
		repopath=os.path.abspath(os.path.join(projectpath,entry['core']['path']))
		git_archive_repo(archivename, os.getcwd(), repopath, entry['core']['sha'])
		
		# addons
		for addon in entry['addons']:
			logger.info('Archiving addon '+addon['name'])
			archivename=str(os.path.basename(projectpath))+'_'+entry['name']+'_'+os.path.basename(addon['name'])+'_'+addon['sha'][0:7]+'.tar.gz'
			repopath=os.path.abspath(os.path.join(projectpath,entry['core']['path'],'addons',addon['name']))
			if addon['sha'] != 'non-git':
				git_archive_repo(archivename, os.getcwd(), repopath, addon['sha'])
			else:
				logger.info(addon['name']+ ' is not a git repo. Packing as tar.gz file.')
				subprocess.call(['tar','-zcf',archivename,'--directory='+os.path.dirname(repopath),os.path.basename(repopath)])

		return 0

###############################################################################
def checkout(args, filename):
	"""Check out a snapshot from a json file, as specified by arguments in args.
	
	Return 0 on success, 1 on failure."""
	logger.debug('In subcommand checkout.')
	basedir=os.getcwd()
	os.chdir(args.project)
	projectpath=os.getcwd()	
	non_git_repos=[]
	
	# open metadata.json, abort on error
	try:
		with open(filename,'r') as metafile:
			json_object = json.load(metafile)
			logger.info('Loaded json data from ' + filename)
			logger.debug(json_object)
	except IOError as e:
			logger.error('Could not open file: ' + str(e))
			return 1
		
	entry = check_for_snapshot_entry(args.name,json_object)
	if not entry:
		logger.error('Snapshot entry '+args.name+' does not exist.')
		return 1

	# make sure all components have clean repos before actual operations, skip non-git
	logger.info('Making sure repos are clean: OF')
	os.chdir(entry['core']['path'])
	if validate_git_repo() !=0:
		logger.error('OF git repo could not be validated successfully.')
		return 1
		
	logger.info('Making sure repos are clean: addons')
	addons_path=os.path.join(os.getcwd(),'addons')
	os.chdir(addons_path)
	for addon in entry['addons']:
			logger.info('Processing addon '+addon['name'])
			if addon['sha'] == 'non-git':
				logger.info('Skipping non-git addon '+addon['name'])
				non_git_repos.append(addon['name'])
			else:
				os.chdir(addon['name'])
				if validate_git_repo() != 0:
					logger.error(addon['name']+' git repo could not be validated successfully.')
					return 1
				os.chdir(addons_path)
	
	logger.info('Checking out openFrameworks')
	# TODO: check for named refs first to avoid unnecessarily detached heads
	logger.info('Checking out '+entry['core']['sha']+' of '+ entry['core']['path'])
	os.chdir(projectpath)
	os.chdir(entry['core']['path'])
	if subprocess.call(['git','checkout',entry['core']['sha']]) != 0:
		logger.error('An error occured checking out '+entry['core']['path'])
		return 1
	
	logger.info('Checking out addons')
	os.chdir(addons_path)
	for addon in entry['addons']:
			if addon['sha'] == 'non-git':
				logger.info('Skipping non-git addon '+addon['name'])
			else:
				logger.info('Checking out '+addon['sha']+' of '+ addon['name'])
				os.chdir(addon['name'])
				if subprocess.call(['git','checkout',addon['sha']]) != 0:
					logger.error('An error occured checking out ' + addon['name'])
					return 1
				os.chdir(addons_path)
	logger.info('Finished checking out snapshot '+entry['name'])
	if non_git_repos:
		logger.warning('The following addons not under git control were found. Correct code state cannot be guaranteed!')
		for item in non_git_repos:
			logger.warning(str(item))
	
	return 0
