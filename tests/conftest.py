# pylint: disable=C0111
import pytest
import os
import tarfile

BASEDIR = os.path.dirname(__file__)


@pytest.fixture(autouse=False)
def set_up(tmpdir):
#    print BASEDIR
    tmpdir.chdir()
    tar = tarfile.open(os.path.join(BASEDIR, "MockRepos.tar.gz"))
    tar.extractall()
    tar.close()
    os.chdir('MockRepos')
    print(('In directory ' + os.getcwd()))
    # does not need teardown, since tmpdir directories get autodeleted


def session_teardown():
    """Tear down testing session"""
    print('Tearing down testing session')
    os.chdir(BASEDIR)  # so html coverage report lands in correct directory


@pytest.fixture(scope='session', autouse=True)
def session_setup(request):
    """Set up testing session"""
    print('Setting up testing session')

    request.addfinalizer(session_teardown)
