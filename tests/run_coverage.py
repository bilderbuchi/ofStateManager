#!/usr/bin/env python
"""Script to collect coverage information on ofStateManager"""

import os
import sys
import inspect
import subprocess


def main():
    """Main function"""
    arguments = ''
    if len(sys.argv) > 1:
        arguments = ' '.join(sys.argv[1:])
    testdir = os.path.abspath(os.path.dirname(
            inspect.getfile(inspect.currentframe())))
    script_path = os.path.join(testdir, '..', 'ofStateManager.py')

    os.environ['COVERAGE_PROCESS_START'] = os.path.join(testdir, '.coveragerc')
    os.environ['COVERAGE_FILE'] = os.path.join(testdir, '.coverage')

    subprocess.call('coverage erase', shell=True, cwd=testdir)
    subprocess.call('coverage run -m py.test ' + arguments,
                    shell=True, cwd=testdir)
    del os.environ['COVERAGE_PROCESS_START']
    subprocess.call('coverage combine', shell=True, cwd=testdir)
    subprocess.call('coverage html -d ' + os.path.join(testdir, 'htmlcov') +
                    ' --include=' + script_path, shell=True, cwd=testdir)
    subprocess.call('coverage report --include=' + script_path,
                    shell=True, cwd=testdir)


if __name__ == '__main__':
    main()
