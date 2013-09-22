"""Tests for the checkout subcommand"""
# pylint: disable=C0111
import pytest
import os
import shutil
from util_functions import SCRIPT_LOC, REPLAY_DIR, script_cmd, load_json_file


@pytest.mark.usefixtures('set_up')
class TestCheckout:
	"""Test checkout subcommand."""

	def test_checkout_no_metadata(self, capfd):
		ret = script_cmd(SCRIPT_LOC + ' checkout -p mockProject', os.getcwd())
		assert ret == 1
		_, err = capfd.readouterr()
		assert 'Could not open file: ' in err

	def test_checkout_no_entry(self, capfd):
		# Create metadata file
		ret = script_cmd(SCRIPT_LOC + ' record -p mockProject', os.getcwd())
		assert ret == 0

		# Try to checkout non-existing entry
		ret = script_cmd(SCRIPT_LOC + ' checkout -p mockProject -n some_name',
						os.getcwd())
		assert ret == 1
		out, err = capfd.readouterr()
		assert 'Loaded json data from metadata.json' in out
		assert 'Snapshot entry some_name does not exist.' in err

	def test_checkout_default(self, capfd):
		# Create metadata file
		ret = script_cmd(SCRIPT_LOC + ' record -p mockProject', os.getcwd())
		assert ret == 0

		# Do a default checkout
		ret = script_cmd(SCRIPT_LOC + ' checkout -p mockProject',
						os.getcwd())
		assert ret == 0
		_, err = capfd.readouterr()
		assert 'git repo could not be validated successfully.' not in err
		assert 'Correct code state cannot be guaranteed!' in err
		assert 'ofxNonGitAddon' in err

	def test_checkout_OF_invalid(self, capfd):
		# Create metadata file
		ret = script_cmd(SCRIPT_LOC + ' record -p mockProject', os.getcwd())
		assert ret == 0

		#Remove OF's .git directory to make checkout validation fail
		shutil.rmtree(os.path.join('mockOF', '.git'))
		# Do a checkout
		ret = script_cmd(SCRIPT_LOC + ' checkout -p mockProject',
						os.getcwd())
		assert ret == 1
		_, err = capfd.readouterr()
		assert 'OF git repo could not be validated successfully.' in err

	def test_checkout_addon_invalid(self, capfd):
		# Create metadata file
		ret = script_cmd(SCRIPT_LOC + ' record -p mockProject', os.getcwd())
		assert ret == 0

		#Remove an addon's .git directory to make checkout validation fail
		shutil.rmtree(os.path.join('mockOF', 'addons', 'ofxSomeAddon', '.git'))
		# Do a checkout
		ret = script_cmd(SCRIPT_LOC + ' checkout -p mockProject',
						os.getcwd())
		assert ret == 1
		_, err = capfd.readouterr()
		assert 'ofxSomeAddon git repo could not be validated successfully.' in err

	def test_checkout_no_nongit(self, capfd):
		# Remove non-git addon from addons.make
		with open(os.path.join('mockProject', 'addons.make'), 'r') as addons_make:
			lines = addons_make.readlines()
		with open(os.path.join('mockProject', 'addons.make'), 'w') as addons_make:
			for line in lines:
				if line.rstrip() != 'ofxNonGitAddon':
					addons_make.write(line)

		# Create metadata file
		ret = script_cmd(SCRIPT_LOC + ' record -p mockProject', os.getcwd())
		assert ret == 0

		# Do a default checkout
		ret = script_cmd(SCRIPT_LOC + ' checkout -p mockProject',
						os.getcwd())
		assert ret == 0
		_, err = capfd.readouterr()
		assert 'git repo could not be validated successfully.' not in err
		assert 'Correct code state cannot be guaranteed!' not in err
		assert 'ofxNonGitAddon' not in err
