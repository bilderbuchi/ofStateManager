"""Tests for the archive subcommand"""
# pylint: disable=C0111
import pytest
import os
from util_functions import run_ofSM

# TODO: git_archive_repo needs to return exist status to verify packing worked.


@pytest.mark.usefixtures('set_up')
class TestArchive:
    """
    Test archive subcommand.
    These do _not_ verify the archive contents against the available files,
    that would be quite complex to test due to git-archive usage.
    """

    def test_archive_default(self, capfd):
        out, _ = run_ofSM('archive -p mockProject', capfd=capfd)
        assert ('Metadata file metadata.json does not exist yet. Creating'
                in out)

    def test_archive_skipping(self, capfd):
        out, _ = run_ofSM('archive -p mockProject', capfd=capfd)
        assert ('Metadata file metadata.json does not exist yet. Creating'
                in out)

        # Do it again to provoke skipping files
        out, _ = run_ofSM('archive -p mockProject', capfd=capfd)
        assert  ' already exists. Skipping ...' in out

    def test_archive_named_snapshot(self, capfd):
        # First, create a metadata file
        out, _ = run_ofSM('record -p mockProject', capfd=capfd)
        assert 'metadata.json does not exist yet. Creating' in out

        # Now, create a named snapshot
        out, _ = run_ofSM('archive -p mockProject -n someName', capfd=capfd)
        assert ('Metadata file metadata.json does not exist yet. Creating'
                not in out)
        assert 'Entry someName does not exist yet. Creating...' in out

    def test_archive_description(self, capfd):
        # First, create an entry with a description
        out, _ = run_ofSM('record -p mockProject -d "my description"',
                          capfd=capfd)
        assert 'metadata.json does not exist yet. Creating' in out

        # Now, archive the "latest" entry
        out, _ = run_ofSM('archive -p mockProject', capfd=capfd)
        assert 'Writing description file' in out
        with open(os.path.join('mockProject', 'mockProject_archive',
                               'mockProject_latest_description.txt'),
                  'r') as descr:
            assert descr.readline() == "my description"

    def test_archive_directory_exists(self, capfd):
        out, _ = run_ofSM('archive -p mockProject', capfd=capfd)
        assert ('Metadata file metadata.json does not exist yet. Creating'
                in out)

        out, _ = run_ofSM('archive -v -p mockProject -n someName', capfd=capfd)
        assert ('Directory mockProject_archive already exists. Continuing.'
                in out)
