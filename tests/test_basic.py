
import os
import pytest
import subprocess
import shlex
import json

# Messy hard-coded script location
script_loc = os.path.abspath(os.path.join(os.path.dirname(__file__),
												os.path.pardir,
												'ofStateManager.py'))
replay_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
												'ReplayData'))

def script_cmd(arg_string, working_dir, return_output=False, log_output=True):
	"""Execute command in repo_dir and log output to LOGGER"""
		# the argument string has to be split if Shell==False in check_output
	output = subprocess.call(shlex.split(arg_string),
								stderr=subprocess.STDOUT, cwd=working_dir)
	return output

def json_replace_date(json_input):
	"""Replace date values in json by dummies to enable meaningful comparison"""
	for item in json_input['snapshots']:
		if item['date']:
			item['date'] = 'removed_date'

def load_json_file(location):
	"""Load json file, replace dates, return json objects"""
	with open(location,'r') as json_fd:
		json_out = json_replace_date(json.load(json_fd))
	return json_out

###############################################################################

@pytest.mark.usefixtures('set_up')
class TestRecord:
	"""Test record subcommand functions"""

	def test_record(self):
		ret = script_cmd(script_loc + ' record -p mockProject', os.getcwd())
		assert ret == 0
		std = load_json_file(os.path.join(replay_dir,'metadata_record.json'))
		test = load_json_file(os.path.join('mockProject','metadata.json'))
		assert test == std

	def test_record_named(self):
		ret = script_cmd(script_loc + ' record -p mockProject -n snapshot-1', os.getcwd())
		assert ret == 0
		std = load_json_file(os.path.join(replay_dir,'metadata_record_snapshot-1.json'))
		test = load_json_file(os.path.join('mockProject','metadata.json'))
		assert test == std


#class TestHelp:
#	"""Test if help text gets printed"""
@pytest.mark.usefixtures('set_up')
def test_help(capfd):
	"""Test if help text gets printed"""
	script_cmd(script_loc + ' --help', os.getcwd())
	out, err = capfd.readouterr()
	assert out.startswith('usage: ofStateManager.py [-h]')
	assert err == ''
