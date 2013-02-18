"""Tests for the help subcommand"""
import os
from util_functions import script_loc, script_cmd


#class TestHelp:
#	"""Test if help text gets printed"""
#@pytest.mark.usefixtures('set_up')
def test_help(capfd):
	"""Test if help text gets printed"""
	script_cmd(script_loc + ' --help', os.getcwd())
	out, err = capfd.readouterr()
	assert out.startswith('usage: ofStateManager.py [-h]')
	assert err == ''
