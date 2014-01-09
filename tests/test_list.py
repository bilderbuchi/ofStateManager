"""Tests for the list subcommand"""
# pylint: disable=C0111
import pytest
from util_functions import run_ofSM

# TODO: list does not check for description existence!


@pytest.mark.usefixtures('set_up')
class TestList:
    """Test list subcommand"""

    def test_list(self, capfd):
        run_ofSM('record -p mockProject')
        out, _ = run_ofSM('list -p mockProject', capfd=capfd)
        assert 'Loaded json data' in out
        assert 'Available snapshots:' in out
        assert 'latest' in out

        out, _ = run_ofSM('list -p mockProject -n latest', capfd=capfd)
        assert 'Loaded json data from' in out
        assert 'Selecting snapshot latest' in out
        assert 'Detailed info for snapshot latest:' in out
        assert 'path: ../mockOF' in out

        out, err = run_ofSM('list -p mockProject -n notexist', capfd=capfd,
                            desired_exit_status=1)
        assert 'Snapshot entry notexist does not exist.' in err

    def test_list_description_latest(self, capfd):
        run_ofSM('record -p mockProject -d "some description"')
        out, _ = run_ofSM('list -p mockProject', capfd=capfd)
        assert 'latest: some description' in out

    def test_list_description_named(self, capfd):
        run_ofSM('record -p mockProject -d "a text" -n dummy')
        out, _ = run_ofSM('list -p mockProject', capfd=capfd)
        assert 'dummy: a text' in out

    def test_list_description_detailed(self, capfd):
        run_ofSM('record -p mockProject -d "a text" -n dummy')
        out, _ = run_ofSM('list -p mockProject -n dummy', capfd=capfd)
        assert 'Detailed info for snapshot dummy:' in out
        assert 'Description: a text' in out
