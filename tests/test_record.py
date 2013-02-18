"""Tests for the record subcommand"""
# pylint: disable=C0111
import pytest
import os
import shutil
from util_functions import SCRIPT_LOC, REPLAY_DIR, script_cmd, load_json_file

# TODO: record with non-existing files just hangs
###############################################################################

## Parameterized test function
#@pytest.mark.usefixtures('set_up')
#@pytest.mark.parametrize(("command", "std_file"), [
#    (SCRIPT_LOC + ' record -p mockProject', 'metadata_record.json'),
#    (SCRIPT_LOC + ' record -p mockProject -n snapshot-1',
#		'metadata_record_snapshot-1.json'),
##    ("6*9", 42),
#])
#def test_json_output(command, std_file):
#	ret = script_cmd(command, os.getcwd())
#	assert ret == 0
#	std = load_json_file(os.path.join(REPLAY_DIR,std_file))
#	test = load_json_file(os.path.join('mockProject','metadata.json'))
#	assert test == std


@pytest.mark.usefixtures('set_up')
#class TestRecord:
#	"""Test record subcommand functions"""
def test_record():
	ret = script_cmd(SCRIPT_LOC + ' record -p mockProject', os.getcwd())
	assert ret == 0
	std = load_json_file(os.path.join(REPLAY_DIR, 'md_record.json'))
	test = load_json_file(os.path.join('mockProject', 'metadata.json'))
	assert test == std


def test_record_remotedir():
	currentdir = os.getcwd()
	os.chdir(os.path.dirname(SCRIPT_LOC))
	ret = script_cmd(os.path.join('./', os.path.basename(SCRIPT_LOC)) +
						' record -p ' + os.path.join(currentdir, 'mockProject'),
					os.getcwd())
	assert ret == 0
	std = load_json_file(os.path.join(REPLAY_DIR, 'md_record.json'))
	test = load_json_file(os.path.join(currentdir, 'mockProject',
									'metadata.json'))
	assert test == std


def test_record_named(capfd):
	ret = script_cmd(SCRIPT_LOC + ' record -p mockProject -n snapshot-1',
					os.getcwd())
	assert ret == 0
	out, err = capfd.readouterr()
	assert 'DEBUG' not in out
	assert 'DEBUG' not in err
	std = load_json_file(os.path.join(REPLAY_DIR, 'md_record_snapshot-1.json'))
	test = load_json_file(os.path.join('mockProject', 'metadata.json'))
	assert test == std


def test_record_verbosity(capfd):
	ret = script_cmd(SCRIPT_LOC + ' record -v -p mockProject -n snapshot-1',
					os.getcwd())
	assert ret == 0
	out, _ = capfd.readouterr()
	assert 'DEBUG' in out

	std = load_json_file(os.path.join(REPLAY_DIR, 'md_record_snapshot-1.json'))
	test = load_json_file(os.path.join('mockProject', 'metadata.json'))
	assert test == std


def test_record_wrong_project(capfd):
	ret = script_cmd(SCRIPT_LOC + ' record -p mockProjectWRONG', os.getcwd())
	assert ret == 1
	_, err = capfd.readouterr()
	# Do this because subprocess does not raise its child's exceptions
	assert 'OSError: [Errno 2]' in err


def test_record_update():
	# copy snapshot-1 metadata file over to mockProject
	shutil.copyfile(os.path.join(REPLAY_DIR, 'md_record_snapshot-1.json'),
					os.path.join('mockProject', 'metadata.json'))
	# this has to bail because -u was not given
	ret = script_cmd(SCRIPT_LOC + ' record -p mockProject -n snapshot-1',
					os.getcwd())
	assert ret == 1
	# this has to work
	ret = script_cmd(SCRIPT_LOC + ' record -u -p mockProject -n snapshot-1',
					os.getcwd())
	assert ret == 0

	std = load_json_file(os.path.join(REPLAY_DIR, 'md_record_snapshot-1.json'))
	test = load_json_file(os.path.join('mockProject', 'metadata.json'))
	assert test == std


def test_record_description():
	ret = script_cmd(SCRIPT_LOC + ' record -p mockProject' +
					' -d "My Test description"', os.getcwd())
	assert ret == 0
	std = load_json_file(os.path.join(REPLAY_DIR, 'md_record_description.json'))
	test = load_json_file(os.path.join('mockProject', 'metadata.json'))
	assert test == std
