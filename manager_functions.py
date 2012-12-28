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
	"""Validate if current directory is in a git repo."""
	
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
			# TODO: this doesn't work with remote, since git repos don't allow clients access to arbitrary sha's, only named ones.
			# solution: go to repo directory, use -o to put into right path
			# cf. http://git.661346.n2.nabble.com/Passing-commit-IDs-to-git-archive-td7359753.html
			# TODO: error catching
			os.chdir(archivepath)

###############################################################################
def record(args):
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
			config_make.close()
			sys.exit('Aborting.')
	
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
				logger.error('error: ' + str(e))
			
		ret= validate_git_repo(strict=False)
		if ret == 0:
			addon['sha'] = subprocess.check_output(['git','rev-parse','HEAD']).strip()
		elif ret == 2:
			addon['sha'] = 'non-git'
		else:
			sys.exit('Aborting.')
	
	logger.info('Storing metadata')
	filename='metadata.json'
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
			logger.error('Could not open file: ' + str(e))
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

###############################################################################
def archive(args):
	logger.debug('In subcommand archive.')
	basedir=os.getcwd()
	os.chdir(args.project)
	projectpath=os.getcwd()	
	filename='metadata.json'
	
	logger.debug('Opening metadata file')
	try:
		with open(filename,'r') as metafile:
			json_object = json.load(metafile)
			logger.info('loaded data from ' + filename)
			logger.debug(json_object)
			# update with data
	except IOError as e:
		if e.errno == errno.ENOENT:
			logger.error('Metadata file ' + filename + ' does not yet exist. Creating...')
			os.chdir(basedir)
			if record(args) == 0:
				os.chdir(basedir)
				return archive(args) # call archive recursively
			else:
				logger.error('Creation of snapshot ' + args.name + 'failed.')
				sys.exit('Aborting')
				return 1
		else:
			logger.error('Error opening metadata file ' + filename + ': ' + str(e))
			sys.exit('Aborting')
			return 1			
		
	# check if snapshot entry already exists
	entry_exists=False
	for entry in json_object['snapshots']:
		if entry['name'] == args.name:
			logger.info('Selecting snapshot '+ args.name)
			entry_exists=True
			break
	if not entry_exists:
		logger.info('Entry ' + args.name + ' does not exist yet. Creating...')
		os.chdir(basedir)
		if record(args) == 0: # call record to create the necessary entry
			os.chdir(basedir)
			return archive(args) # call archive recursively
		else:
			logger.error('Creation of snapshot ' + args.name + 'failed.')
			sys.exit('Aborting')
			return 1
	#--------------------------------------------------------------------------
	else:
		# entry exists, start archiving
		# create subdirectory for archive
		archivedirectory=os.path.basename(projectpath)+'_archive'
		try:
			os.mkdir(archivedirectory)
		except OSError as e:
			if e.errno != errno.EEXIST:
				logger.error('Could not create directory: ' + archivedirectory + ': ' + str(e))
				sys.exit('Aborting')
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
def checkout(args):
	logger.debug('In subcommand checkout.')
	basedir=os.getcwd()
	os.chdir(args.project)
	projectpath=os.getcwd()	
	filename='metadata.json'
	
	# open metadata.json, abort on error
	# search for entry, if unknown abort
	# parse entry
	# make sure all components have clean repos, skip non-git
	# checkout given sha, skip non-git
	# warn about unknown non-git components 
	
	logger.error('This is not yet implemented.')
	sys.exit('Aborting')
	return 0




