"""Tests for the record subcommand"""
# pylint: disable=C0111
import pytest
import os
import shutil
from util_functions import SCRIPT_LOC, REPLAY_DIR, script_cmd, load_json_file
from util_functions import run_ofSM

# TODO: record with non-existing files just hangs
###############################################################################


@pytest.mark.usefixtures('set_up')
class TestRecord:
    """Test record subcommand functions"""

    def test_record(self):
        run_ofSM('record -p mockProject')
        std = load_json_file(os.path.join(REPLAY_DIR, 'md_record.json'))
        test = load_json_file(os.path.join('mockProject', 'metadata.json'))
        assert test == std

    def test_record_remotedir(self):
        currentdir = os.getcwd()
        os.chdir(os.path.dirname(SCRIPT_LOC))
        ret = script_cmd(
            os.path.join('./', os.path.basename(SCRIPT_LOC)) + ' record -p ' +
            os.path.join(currentdir, 'mockProject'),
            os.getcwd())
        assert ret == 0
        std = load_json_file(os.path.join(REPLAY_DIR, 'md_record.json'))
        test = load_json_file(os.path.join(currentdir, 'mockProject',
                                        'metadata.json'))
        assert test == std

    def test_record_default_p_dir(self):
        currentdir = os.getcwd()
        os.chdir('mockProject')
        run_ofSM('record')
        std = load_json_file(os.path.join(REPLAY_DIR, 'md_record.json'))
        test = load_json_file(os.path.join(currentdir, 'mockProject',
                                        'metadata.json'))
        assert test == std

    def test_record_named(self, capfd):
        out, err = run_ofSM('record -p mockProject -n snapshot-1', capfd=capfd)
        assert 'DEBUG' not in out
        assert 'DEBUG' not in err
        std = load_json_file(os.path.join(REPLAY_DIR,
                                          'md_record_snapshot-1.json'))
        test = load_json_file(os.path.join('mockProject', 'metadata.json'))
        assert test == std

    def test_record_verbosity(self, capfd):
        out, _ = run_ofSM('record -v -p mockProject -n snapshot-1',
                          capfd=capfd)
        assert 'DEBUG' in out

        std = load_json_file(os.path.join(REPLAY_DIR,
                                          'md_record_snapshot-1.json'))
        test = load_json_file(os.path.join('mockProject', 'metadata.json'))
        assert test == std

    def test_record_wrong_project(self, capfd):
        _, err = run_ofSM('record -p mockProjectWRONG', capfd=capfd,
                          desired_exit_status=1)
        # Do this because subprocess does not raise its child's exceptions
        assert 'OSError: [Errno 2]' in err

    def test_record_update(self):
        # copy snapshot-1 metadata file over to mockProject
        shutil.copyfile(os.path.join(REPLAY_DIR, 'md_record_snapshot-1.json'),
                        os.path.join('mockProject', 'metadata.json'))
        # this has to bail because -u was not given
        run_ofSM('record -p mockProject -n snapshot-1', desired_exit_status=1)
        # this has to work
        run_ofSM('record -u -p mockProject -n snapshot-1')

        std = load_json_file(os.path.join(REPLAY_DIR,
                                          'md_record_snapshot-1.json'))
        test = load_json_file(os.path.join('mockProject', 'metadata.json'))
        assert test == std

    def test_record_description(self):
        run_ofSM('record -p mockProject -d "My Test description"')
        std = load_json_file(os.path.join(REPLAY_DIR,
                                          'md_record_description.json'))
        test = load_json_file(os.path.join('mockProject', 'metadata.json'))
        assert test == std

    def test_record_empty_addons_make(self, capfd):
        fobj = open(os.path.join(os.getcwd(), 'mockProject', 'addons.make'),
                    'w')
        fobj.close()
        out, _ = run_ofSM('record -p mockProject', capfd=capfd)
        assert 'No addons found.' in out

    def test_record_no_OF_location(self, capfd):
        fobj = open(os.path.join(os.getcwd(), 'mockProject', 'config.make'),
                    'w')
        fobj.close()
        _, err = run_ofSM('record -p mockProject', capfd=capfd,
                          desired_exit_status=1)
        assert 'Did not find OF location in config.make in' in err

    def test_record_addon_nonexistent(self, capfd):
        shutil.rmtree(os.path.join('mockOF', 'addons', 'ofxSomeAddon'))
        _, err = run_ofSM('record -p mockProject', capfd=capfd,
                          desired_exit_status=1)
        assert 'ofxSomeAddon does not exist at' in err
        assert err.endswith('Aborting\n')

    def test_record_addon_invalid(self, capfd):
        open(os.path.join(os.getcwd(), 'mockOF', 'addons', 'ofxSomeAddon',
                        'untracked.txt'), 'w').close()
        _, err = run_ofSM('record -p mockProject', capfd=capfd,
                          desired_exit_status=1)
        assert 'Repository has untracked files' in err

    def test_record_no_addonsmake(self, capfd):
        os.remove(os.path.join(os.getcwd(), 'mockProject', 'addons.make'))
        out, _ = run_ofSM('record -v -p mockProject', capfd=capfd)
        assert 'No addons.make file found.' in out
