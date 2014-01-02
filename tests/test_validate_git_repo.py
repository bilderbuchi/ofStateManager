"""Tests for validate_git_repo"""
# pylint: disable=C0111
import pytest
import os
from util_functions import SCRIPT_LOC, script_cmd


@pytest.mark.usefixtures('set_up')
class TestValidateGitRepo:
    """Test validate_git_repo()"""

    def test_validate_repo_untracked(self, capfd):
        open(os.path.join(os.getcwd(), 'mockOF', 'untracked.txt'), 'w').close()
        ret = script_cmd(SCRIPT_LOC + ' record -p mockProject', os.getcwd())
        assert ret == 1
        _, err = capfd.readouterr()
        assert 'Repository has untracked files' in err

    def test_validate_repo_uncommitted(self, capfd):
        open(os.path.join(os.getcwd(), 'mockOF', 'somOfFile.txt'), 'w').close()
        ret = script_cmd(SCRIPT_LOC + ' record -p mockProject', os.getcwd())
        assert ret == 1
        _, err = capfd.readouterr()
        assert 'Repository has uncommitted changes' in err
