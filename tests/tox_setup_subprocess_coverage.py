#!/usr/bin/env python
# tox does not implement shell semantics, so we use python to create a file

with open('subproc.pth', 'w') as fobj:
    fobj.write('import coverage; coverage.process_startup()\n')
