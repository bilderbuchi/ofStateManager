import pytest
import tempfile
import os
import tarfile

basedir = os.path.dirname(__file__)

@pytest.fixture()
def set_up(tmpdir):
#	print basedir
	tmpdir.chdir()
	tar = tarfile.open(os.path.join(basedir, "MockRepos.tar.gz"))
	tar.extractall()
	tar.close()
	os.chdir('MockRepos')
	print('In directory ' + os.getcwd())
	# does not need teardown, since tmpdir directories get autodeleted
