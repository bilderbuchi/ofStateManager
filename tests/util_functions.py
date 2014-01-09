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
    """Execute command in working_dir and return output"""
    output = subprocess.call(shlex.split(arg_string),
                                stderr=subprocess.STDOUT, cwd=working_dir)
    return output


def run_ofSM(option_string='', capfd=None, desired_exit_status=0):
    """
    Run ofStateManager in current directory, perform exit status check.

    Also takes an option string, and can return stdout and stderr if
    pytest capfd is passed.
    """
    exit_status = script_cmd(SCRIPT_LOC + ' ' + option_string, os.getcwd())
    assert exit_status == desired_exit_status
    if capfd:
        out, err = capfd.readouterr()
        return out, err


def json_replace_date(json_input):
    """Replace date values in json by dummy to enable meaningful comparison"""
    for item in json_input['snapshots']:
        if item['date']:
            item['date'] = 'removed_date'
    return json_input


def load_json_file(location):
    """Load json file, replace dates, return json objects"""
    with open(location, 'r') as json_fd:
        json_out = json_replace_date(json.load(json_fd))
    return json_out
