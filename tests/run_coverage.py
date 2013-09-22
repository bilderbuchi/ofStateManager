#!/usr/bin/env python
import os
import sys
import inspect
import coverage
import subprocess

arguments = ''
if len(sys.argv) > 1:
	arguments = ' '.join(sys.argv[1:])

testdir = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))
os.environ['COVERAGE_PROCESS_START'] = os.path.join(testdir, '.coveragerc')
os.environ['COVERAGE_FILE'] = os.path.join(testdir, '.coverage')
cov = coverage.coverage(source=os.path.join(testdir, '..'),
					include=os.path.join(testdir, '..', 'ofStateManager.py'))

cov.erase()
subprocess.call('coverage run -m py.test ' + arguments, shell=True, cwd=testdir)
cov.combine()
cov.html_report(directory=os.path.join(testdir, 'htmlcov'))
cov.report(show_missing=False)
