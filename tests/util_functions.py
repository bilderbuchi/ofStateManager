"""Utility functions for testing of ofStateManager"""
import os
import json
import subprocess
import shlex

# Messy hard-coded script location
SCRIPT_LOC = os.path.abspath(os.path.join(os.path.dirname(__file__),
												os.path.pardir,
												'ofStateManager.py'))
REPLAY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
												'ReplayData'))


def script_cmd(arg_string, working_dir):
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
	return json_input


def load_json_file(location):
	"""Load json file, replace dates, return json objects"""
	with open(location, 'r') as json_fd:
		json_out = json_replace_date(json.load(json_fd))
	return json_out
