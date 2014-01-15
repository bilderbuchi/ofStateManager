#!/usr/bin/env python

import sys
# Check for correct Python version
if (sys.version_info < (2, 7)) or (sys.version_info >= (3, 0)):
    print("This package needs Python 2.7 to run.")
    sys.exit(1)

#from ez_setup import use_setuptools
#use_setuptools()
from setuptools import setup
from setuptools.command.test import test as TestCommand


# to install: ./setup.py install
# use the --user flag to install for current user only (recommended)
# Note: this will install setuptools >=2.0.2 if not yet available on the system
#
# to run tests: ./setup.py test
# to install in develop mode: ./setup.py develop --user

# You should inform your users that if they are installing your project to
# somewhere other than the main site-packages directory, they should first
# install setuptools using the instructions for Custom Installation Locations,
# before installing your project.
# Note, however, that they must still install those projects using easy_install
# , or your project will not know they are installed, and your setup script
# will try to download them again.)


# calling py.test
class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        # to make sure py.test only runs test in /tests directory in virtualenv
        arglist = list(self.test_args)
        arglist.append('tests')
        errno = pytest.main(arglist)
        sys.exit(errno)


setup(name='ofStateManager',
      version='1.0',
      description=('Leverages git to help you organize and archive ' +
                   'your openFrameworks projects'),
      author='Christoph Buchner',
      url='https://github.com/bilderbuchi/ofStateManager',
      cmdclass={'test': PyTest},
      scripts=['ofStateManager.py'],
#      requires=['argparse'], # dropped because included in python 2.7
      extras_require={'test': ['pytest>=2.3.4', 'coverage']}
#      tests_require=['pytest>=2.3.4', 'coverage'],
     )
