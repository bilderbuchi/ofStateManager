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
      version='1.0.1',
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
