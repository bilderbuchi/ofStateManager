#!/usr/bin/python
import logging
import argparse
import sys
import os
import subprocess
import json
import errno
from datetime import datetime

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
		# check for uncommitted modifications
		# apparently --quiet is not 100% reliable. Use --exit-code instead
		if subprocess.call('git diff --exit-code HEAD > /dev/null', shell=True) != 0:
			logger.error('Repository has uncommitted changes, commit those before continuing!')
			return 1
		else:
			# Check for untracked files
			if not subprocess.call('git ls-files --others --exclude-standard --error-unmatch . > /dev/null 2>&1',shell=True):
				logger.error('Repository has untracked files, either commit, ignore or delete them.')
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
	
	logger.info('Processing OF at '+OF_path)
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
				logger.error(addon['name'] + ' does not exist at ' + addons_path + '.')
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
	temp= {'name': args.name, 'date': datetime.now().isoformat(), 'description': args.description, 'core': core_dict, 'addons': addons_list}
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
			setattr(args, 'description', '')
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
		setattr(args, 'description', '')
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
		basename=str(os.path.basename(projectpath))
		archivedirectory=basename+'_archive'
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
		# Description file
		if entry['description'] != '':
			logger.info('Writing description file')
			with open(basename+'_'+entry['name']+'_description.txt','w') as descriptionfile:
				descriptionfile.write(entry['description'])
			
		# OF itself
		archivename=basename+'_'+entry['name']+'_OF_'+entry['core']['sha'][0:7]+'.tar.gz'
		repopath=os.path.abspath(os.path.join(projectpath,entry['core']['path']))
		git_archive_repo(archivename, os.getcwd(), repopath, entry['core']['sha'])
		
		# addons
		for addon in entry['addons']:
			logger.info('Archiving addon '+addon['name'])
			archivename=basename+'_'+entry['name']+'_'+os.path.basename(addon['name'])+'_'+addon['sha'][0:7]+'.tar.gz'
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

###############################################################################
def list(args, filename):
	"""List available snapshots. If a snapshot name is supplied, give more detailed info.
	
	Return 0 on success, 1 on failure."""
	
	logger.debug('In subcommand list.')
	basedir=os.getcwd()
	os.chdir(args.project)
	projectpath=os.getcwd()
	
	with open(filename,'r') as metafile:
		json_object = json.load(metafile)
		logger.info('Loaded json data from ' + filename)
		logger.debug(json_object)
	
	if args.name_was_given:
		entry = check_for_snapshot_entry(args.name,json_object)
		if not entry:
			logger.error('Snapshot entry ' + args.name + ' does not exist.')
			return 1
		else:
			logger.info('Detailed info for snapshot '+entry['name']+':')
			if entry['description'] != '':
				logger.info('Description: '+ entry['description'])
			logger.info('Date: '+entry['date'])
			logger.info('Openframeworks:')
			logger.info('  path: '+entry['core']['path'])
			logger.info('  SHA: '+entry['core']['sha'])
			logger.info('Addons:')
			for addon in entry['addons']:
				logger.info('  name: '+addon['name'])
				logger.info('  SHA: '+addon['sha'])
			return 0
	else:
		logger.info('Available snapshots:')
		for s in json_object['snapshots']:
			temp_string='  '+s['name']
			if s['description'] != '':
				temp_string+=(': '+s['description'])
			logger.info(temp_string)
		logger.info('Get more information by specifying desired snapshot with -n <name>.')
		return 0

###############################################################################
class LessThanLevelFilter(logging.Filter):
	def __init__(self, passlevel):
		self.passlevel = passlevel
	def filter(self, record):
		return (record.levelno < self.passlevel)

###############################################################################
def main():
	
	# Set up logging
	my_format = "%(levelname)s\t%(message)s"
	#Warning and above goes to stderr
	eh = logging.StreamHandler(sys.stderr)
	eh.setFormatter(logging.Formatter(my_format))
	eh.setLevel(logging.WARNING)
	# everything from Debug to Info goes to stdout
	sh = logging.StreamHandler(sys.stdout)
	sh.setFormatter(logging.Formatter(my_format))
	sh.setLevel(logging.DEBUG)
	sh.addFilter(LessThanLevelFilter(logging.WARNING))
	logger.addHandler(eh)
	logger.addHandler(sh)
	
	#*************************************
	# command line argument parser
	parser = argparse.ArgumentParser(description='Record and restore the state of your openFrameworks projects and archive their files.')
	#Parent parser contains common options
	parent_parser = argparse.ArgumentParser(add_help=False)
	parent_parser.add_argument('-p', '--project', default=os.getcwd(), help='Path to the desired project directory, defaults to the current directory if this option is not given')
	parent_parser.add_argument('-n', '--name', help='Name of the desired snapshot. Defaults to "latest", except when using list.')
	parent_parser.add_argument('-v', '--verbose', action='store_true', help='Switch on debug logging.')
	
	subparsers = parser.add_subparsers(help='Available commands')
	record_parser = subparsers.add_parser('record', help='Record the state of all relevant components into a snapshot', parents=[parent_parser])
	record_parser.add_argument('-u', '--update', action='store_true', help='If name already exists, overwrite existing entry')
	record_parser.add_argument('-d', '--description', default='', help='Short message describing the snapshot in more detail than the name. Do not forget " " around DESCRIPTION if it contains whitespace.')
	record_parser.set_defaults(func=record)
	
	checkout_parser = subparsers.add_parser('checkout', help='Check out the complete named or latest snapshot of your project and OF', parents=[parent_parser])
	checkout_parser.set_defaults(func=checkout)
	
	archive_parser = subparsers.add_parser('archive', help='Archive all relevant components for the named or latest snapshot', parents=[parent_parser])
	archive_parser.set_defaults(func=archive)
	
	list_parser = subparsers.add_parser('list', help='List available snapshots. -n gives more detailed info about named snapshot', parents=[parent_parser])
	list_parser.set_defaults(func=list)
	
	args=parser.parse_args()
#	args=parser.parse_args('archive -p tests/mockTree/mockProject1 -n somesnaptohs -v'.split()) #pass '-xyzZ'.split() for debugging
	
	# Manual defaults for name, to enable correct parsing in list()
	if not args.name:
		setattr(args, 'name', 'latest')
		setattr(args, 'name_was_given', False)
	else:
		setattr(args, 'name_was_given', True)
	
	#Verify option/argument validity
	#TODO: verification routines
	
	# Initialisation
	if args.verbose is True:
		logger.setLevel(logging.DEBUG)
		# more detailed error messages for verbose mode
		my_format = "%(levelname)s\t%(funcName)s: %(message)s"
		sh.setFormatter(logging.Formatter(my_format))
		eh.setFormatter(logging.Formatter(my_format))
	else:
		logger.setLevel(logging.INFO) # DEBUG/INFO/WARNING/ERROR/CRITICAL
	
	logger.debug(args)
	metadata_filename='metadata.json' # file where metadata about project resides
	logger.debug('Metadata filename: ' + metadata_filename)
	
	#Main function
	logger.info('Start processing.')
	ret = args.func(args,metadata_filename)
	if  ret != 0:
		logger.critical('An error occurred! Aborting execution.')
	else:
		logger.info('Successfully finished processing!')
	
	#Cleanup
	logging.shutdown()
	return ret

###############################################################################
if __name__ == '__main__':
	logger = logging.getLogger('OFStateMgr')
	ret = main()
	sys.exit(ret)
