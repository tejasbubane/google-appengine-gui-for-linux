#!/usr/bin/env python
#
# Copyright 2008 Google Inc.  All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Run unit tests for the launcher, generating code coverage.

   With no args: run all tests.
   With filename(s) as an arg(s): just those tests

   Temporary solution until the new test runner lands.
"""

import os
import sys
import re


# Common setup
PYTHON = sys.executable
ROOTDIR = sys.path[0]
COVERAGE = None
os.environ['COVERAGE_FILE'] = 'coverage.out'

# Setup our subprocess environment
if os.name == 'posix':
  if os.uname()[0] in ('Darwin', 'Linux'):
    COVSCRIPT = '../../../../google3/third_party/coverage/python/coverage.py'
    COVERAGE = os.path.join(ROOTDIR, COVSCRIPT)
    os.environ['PYTHONPATH'] = '.:../../../../googleclient/third_party/py/mox'
  else:
    print "Please don't use cygwin's python for this script"
    sys.exit(1)
elif os.name == 'nt':
  COVSCRIPT = '../../../../google3/third_party/coverage/python/coverage.py.2.8'
  COVERAGE=os.path.join(ROOTDIR, COVSCRIPT)
  os.environ['PYTHONPATH'] = '.;..\\..\\..\\..\\googleclient\\third_party\\py\\mox'


# Find test files, either specified on the command line or
# anything we can find.
UNITTEST_FILES = []
SOURCE_FILES = []
if len(sys.argv) > 1:
  UNITTEST_FILES = sys.argv[1:]
else:
  contents = [ROOTDIR + '/' + x for x in os.listdir(ROOTDIR)]
  parent = os.path.join(ROOTDIR, 'launcher')
  contents += [parent + '/' + x for x in os.listdir(parent)]
  for file in contents:
    if file.endswith('_unittest.py'):
      UNITTEST_FILES.append(file)
    elif file.endswith('.py'):
      source = os.path.splitext(file)[0] + '_unittest.py'
      if os.path.exists(source):
        # We only care about source files that have unit tests
        SOURCE_FILES.append('"' + file + '"')

# Run all unit tests, keeping track of failures
FAILURES = 0
for utfile in UNITTEST_FILES:
  print utfile
  status = os.system('%s "%s" -x "%s"' % (PYTHON, COVERAGE, utfile))
  if status != 0:
    FAILURES += 1

# Summarize results and remove temp files
os.system('%s "%s" -c' % (PYTHON, COVERAGE))
if SOURCE_FILES:
  os.system('%s "%s" -r %s' % (PYTHON, COVERAGE, ' '.join(SOURCE_FILES)))

# Delete coverage files
FILENAME_RE = re.compile('/coverage.out.(\\d)+$')
for filename in [ROOTDIR + '/' + x for x in os.listdir(ROOTDIR)]:
  if FILENAME_RE.search(filename):
    os.remove(filename)

if FAILURES:
  print '------------------------'
  print '  TOTAL FAILURES: %d' % FAILURES
  print '------------------------'
  sys.exit(1)
