"""Tests for the archive subcommand"""
# pylint: disable=C0111
import pytest
import os
from util_functions import SCRIPT_LOC, REPLAY_DIR, script_cmd, load_json_file

# TODO: git_archive_repo needs to return exist status to verify packing worked.

@pytest.mark.usefixtures('set_up')
class TestArchive:
	"""Test archive subcommand.
	These do _not_ verify the archive contents against	the available files,
	that would be quite complex to test due to git-archive usage. """

	def test_archive_default(self, capfd):
		ret = script_cmd(SCRIPT_LOC + ' archive -p mockProject', os.getcwd())
		assert ret == 0
		out, _ = capfd.readouterr()
		assert 'Metadata file metadata.json does not yet exist. Creating' in out
