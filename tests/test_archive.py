"""Tests for the archive subcommand"""
# pylint: disable=C0111
import pytest
import os
from util_functions import SCRIPT_LOC, script_cmd

# TODO: git_archive_repo needs to return exist status to verify packing worked.


@pytest.mark.usefixtures('set_up')
class TestArchive:
    """
    Test archive subcommand.
    These do _not_ verify the archive contents against the available files,
    that would be quite complex to test due to git-archive usage.
    """

    def test_archive_default(self, capfd):
        ret = script_cmd(SCRIPT_LOC + ' archive -p mockProject', os.getcwd())
        assert ret == 0
        out, _ = capfd.readouterr()
        assert 'Metadata file metadata.json does not yet exist. Creating' in out

    def test_archive_skipping(self, capfd):
        ret = script_cmd(SCRIPT_LOC + ' archive -p mockProject', os.getcwd())
        assert ret == 0
        out, _ = capfd.readouterr()
        assert 'Metadata file metadata.json does not yet exist. Creating' in out

        # Do it again to provoke skipping files
        ret = script_cmd(SCRIPT_LOC + ' archive -p mockProject', os.getcwd())
        assert ret == 0
        out, _ = capfd.readouterr()
        assert  ' already exists. Skipping ...' in out

    def test_archive_named_snapshot(self, capfd):
        # First, create a metadata file
        ret = script_cmd(SCRIPT_LOC + ' record -p mockProject', os.getcwd())
        assert ret == 0
        out, _ = capfd.readouterr()
        assert 'metadata.json does not exist. Creating' in out

        # Now, create a named snapshot
        ret = script_cmd(SCRIPT_LOC + ' archive -p mockProject -n someName',
                        os.getcwd())
        assert ret == 0
        out, _ = capfd.readouterr()
        assert 'Metadata file metadata.json does not yet exist. Creating' not in out
        assert 'Entry someName does not exist yet. Creating...' in out

    def test_archive_description(self, capfd):
        # First, create an entry with a description
        ret = script_cmd(SCRIPT_LOC + ' record -p mockProject -d "my description"',
                        os.getcwd())
        assert ret == 0
        out, _ = capfd.readouterr()
        assert 'metadata.json does not exist. Creating' in out

        # Now, archive the "latest" entry
        ret = script_cmd(SCRIPT_LOC + ' archive -p mockProject', os.getcwd())
        assert ret == 0
        out, _ = capfd.readouterr()
        assert 'Writing description file' in out
        with open(os.path.join('mockProject', 'mockProject_archive',
                            'mockProject_latest_description.txt'), 'r') as descr:
            assert descr.readline() == "my description"

    def test_archive_directory_exists(self, capfd):
        ret = script_cmd(SCRIPT_LOC + ' archive -p mockProject', os.getcwd())
        assert ret == 0
        out, _ = capfd.readouterr()
        assert 'Metadata file metadata.json does not yet exist. Creating' in out

        ret = script_cmd(SCRIPT_LOC + ' archive -v -p mockProject -n someName',
                        os.getcwd())
        assert ret == 0
        out, _ = capfd.readouterr()
        assert 'Directory mockProject_archive already exists. Continuing.' in out
