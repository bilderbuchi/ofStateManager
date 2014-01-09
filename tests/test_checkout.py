"""Tests for the checkout subcommand"""
# pylint: disable=C0111
import pytest
import os
import shutil
import subprocess
from util_functions import run_ofSM


@pytest.mark.usefixtures('set_up')
class TestCheckout:
    """Test checkout subcommand."""

    def test_checkout_no_metadata(self, capfd):
        _, err = run_ofSM('checkout -p mockProject', capfd=capfd,
                          desired_exit_status=1)
        assert 'Could not open file: ' in err

    def test_checkout_no_entry(self, capfd):
        # Create metadata file
        run_ofSM('record -p mockProject')

        # Try to checkout non-existing entry
        out, err = run_ofSM('checkout -p mockProject -n some_name',
                            capfd=capfd, desired_exit_status=1)
        assert 'Loaded json data from metadata.json' in out
        assert 'Snapshot entry some_name does not exist.' in err

    def test_checkout_default(self, capfd):
        # Create metadata file
        run_ofSM('record -p mockProject')

        # Do a default checkout
        _, err = run_ofSM('checkout -p mockProject', capfd=capfd)
        assert 'git repo could not be validated successfully.' not in err
        assert 'Correct code state cannot be guaranteed!' in err
        assert 'ofxNonGitAddon' in err

    def test_checkout_OF_invalid(self, capfd):
        # Create metadata file
        run_ofSM('record -p mockProject')

        #Remove OF's .git directory to make checkout validation fail
        shutil.rmtree(os.path.join('mockOF', '.git'))
        # Do a checkout
        _, err = run_ofSM('checkout -p mockProject', capfd=capfd,
                          desired_exit_status=1)
        assert 'OF git repo could not be validated successfully.' in err

    def test_checkout_addon_invalid(self, capfd):
        # Create metadata file
        run_ofSM('record -p mockProject')

        #Remove an addon's .git directory to make checkout validation fail
        shutil.rmtree(os.path.join('mockOF', 'addons', 'ofxSomeAddon', '.git'))
        # Do a checkout
        _, err = run_ofSM('checkout -p mockProject', capfd=capfd,
                          desired_exit_status=1)
        assert ('ofxSomeAddon git repo could not be validated successfully.'
                in err)

    def test_checkout_no_nongit(self, capfd):
        # Remove non-git addon from addons.make
        with open(os.path.join('mockProject', 'addons.make'), 'r') as fobj:
            lines = fobj.readlines()
        with open(os.path.join('mockProject', 'addons.make'), 'w') as fobj:
            for line in lines:
                if line.rstrip() != 'ofxNonGitAddon':
                    fobj.write(line)

        # Create metadata file
        run_ofSM('record -p mockProject')

        # Do a default checkout
        _, err = run_ofSM('checkout -p mockProject', capfd=capfd)
        assert 'git repo could not be validated successfully.' not in err
        assert 'Correct code state cannot be guaranteed!' not in err
        assert 'ofxNonGitAddon' not in err

    def test_checkout_head_detached(self, capfd):
        # Create metadata file
        run_ofSM('record -p mockProject')

        # Check it out again, assert that there's no detached HEAD
        out, err = run_ofSM('checkout -v -p mockProject', capfd=capfd)
        assert "You are in 'detached HEAD' state" not in out
        assert "You are in 'detached HEAD' state" not in err

    def test_checkout_head_should_be_detached(self, capfd):
        # detach the head of OF
        os.chdir('mockOF')
        ret = subprocess.call(['git', 'checkout', 'HEAD^1'])
        assert ret == 0
        os.chdir('..')

        # Create metadata file
        run_ofSM('record -p mockProject')

        # reattach the head of OF
        os.chdir('mockOF')
        ret = subprocess.call(['git', 'checkout', 'master'])
        assert ret == 0
        _, _ = capfd.readouterr()
        os.chdir('..')

        # Check it out again, assert that there's a detached HEAD now
        _, err = run_ofSM('checkout -p mockProject', capfd=capfd)
        assert "You are in 'detached HEAD' state" in err
