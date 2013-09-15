"""Tests for the list subcommand"""
# pylint: disable=C0111
import pytest
import os
from util_functions import SCRIPT_LOC, script_cmd

# TODO: list does not check for description existence!


@pytest.mark.usefixtures('set_up')
class TestList:
	"""Test list subcommand"""

	def test_list(self, capfd):
		ret = script_cmd(SCRIPT_LOC + ' record -p mockProject', os.getcwd())
		assert ret == 0
		ret = script_cmd(SCRIPT_LOC + ' list -p mockProject', os.getcwd())
		assert ret == 0
		out, _ = capfd.readouterr()
		assert 'Loaded json data' in out
		assert 'Available snapshots:' in out
		assert 'latest' in out

		ret = script_cmd(SCRIPT_LOC + ' list -p mockProject -n latest', os.getcwd())
		assert ret == 0
		out, _ = capfd.readouterr()
		assert 'Loaded json data from' in out
		assert 'Selecting snapshot latest' in out
		assert 'Detailed info for snapshot latest:' in out
		assert 'path: ../mockOF' in out

		ret = script_cmd(SCRIPT_LOC + ' list -p mockProject -n notexist', os.getcwd())
		assert ret == 1
		out, err = capfd.readouterr()
		assert 'Snapshot entry notexist does not exist.' in err
