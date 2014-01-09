"""Tests for validate_git_repo"""
# pylint: disable=C0111
import pytest
import os
from util_functions import run_ofSM


@pytest.mark.usefixtures('set_up')
class TestValidateGitRepo:
    """Test validate_git_repo()"""

    def test_validate_repo_untracked(self, capfd):
        open(os.path.join(os.getcwd(), 'mockOF', 'untracked.txt'), 'w').close()
        _, err = run_ofSM('record -p mockProject', capfd=capfd,
                          desired_exit_status=1)
        assert 'Repository has untracked files' in err

    def test_validate_repo_uncommitted(self, capfd):
        open(os.path.join(os.getcwd(), 'mockOF', 'somOfFile.txt'), 'w').close()
        _, err = run_ofSM('record -p mockProject', capfd=capfd,
                          desired_exit_status=1)
        assert 'Repository has uncommitted changes' in err
