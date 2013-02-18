
import os
import pytest
import subprocess
import shlex
import shutil
import json
from utility_functions import *

###############################################################################

## Parameterized test function
#@pytest.mark.usefixtures('set_up')
#@pytest.mark.parametrize(("command", "std_file"), [
#    (script_loc + ' record -p mockProject', 'metadata_record.json'),
#    (script_loc + ' record -p mockProject -n snapshot-1', 'metadata_record_snapshot-1.json'),
##    ("6*9", 42),
#])
#def test_json_output(command, std_file):
#	ret = script_cmd(command, os.getcwd())
#	assert ret == 0
#	std = load_json_file(os.path.join(replay_dir,std_file))
#	test = load_json_file(os.path.join('mockProject','metadata.json'))
#	assert test == std


@pytest.mark.usefixtures('set_up')
#class TestRecord:
#	"""Test record subcommand functions"""
def test_record():
	ret = script_cmd(script_loc + ' record -p mockProject', os.getcwd())
	assert ret == 0
	std = load_json_file(os.path.join(replay_dir,'metadata_record.json'))
	test = load_json_file(os.path.join('mockProject','metadata.json'))
	assert test == std

def test_record_named():
	ret = script_cmd(script_loc + ' record -p mockProject -n snapshot-1', os.getcwd())
	assert ret == 0
	std = load_json_file(os.path.join(replay_dir,'metadata_record_snapshot-1.json'))
	test = load_json_file(os.path.join('mockProject','metadata.json'))
	assert test == std

def test_record_wrong_project(capfd):
	ret = script_cmd(script_loc + ' record -p mockProjectWRONG', os.getcwd())
	assert ret == 1
	out, err = capfd.readouterr()
	# Do this because subprocess does not raise its child's exceptions
	assert 'OSError: [Errno 2]' in err

def test_record_update():
	# copy snapshot-1 metadata file over to mockProject
	shutil.copyfile(os.path.join(replay_dir, 'metadata_record_snapshot-1.json'),
					os.path.join('mockProject', 'metadata.json'))
	# this has to bail because -u was not given
	ret = script_cmd(script_loc + ' record -p mockProject -n snapshot-1', os.getcwd())
	assert ret == 1
	# this has to work
	ret = script_cmd(script_loc + ' record -u -p mockProject -n snapshot-1', os.getcwd())
	assert ret == 0

	std = load_json_file(os.path.join(replay_dir,'metadata_record_snapshot-1.json'))
	test = load_json_file(os.path.join('mockProject','metadata.json'))
	assert test == std

#class TestHelp:
#	"""Test if help text gets printed"""
#@pytest.mark.usefixtures('set_up')
def test_help(capfd):
	"""Test if help text gets printed"""
	script_cmd(script_loc + ' --help', os.getcwd())
	out, err = capfd.readouterr()
	assert out.startswith('usage: ofStateManager.py [-h]')
	assert err == ''
