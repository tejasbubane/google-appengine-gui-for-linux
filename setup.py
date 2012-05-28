#!/usr/bin/env python
#
# Copyright 2008 Google Inc.
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

# Execute "python setup.py py2exe" to build a stand-alone Windows
# executable in "./dist".  Including everything (python wx, etc), the
# windows exe is currently 16M (8M when zipped).  The breakdown of
# size is approximately:
#   10M for wx (object code)
#    2M for python (object code)
#    4M for everything else (including all embedded python code)
# This does not include the SDK.
#
# By comparison, the Mac launcher (which includes the SDK) is 2.6M compressed.

import glob
import os
from distutils.core import setup

if os.name == 'nt':
  import py2exe

# Use this to ignore some of the many wx dlls we don't need:
#  options = {"py2exe": { "dll_excludes": ["foobar.dll"]}},

setup(
  windows=[{
      # List of scripts to convert into gui exes
      'script': 'GoogleAppEngineLauncher.py',
      # Icon resources
      'icon_resources': [(1, 'appengine.ico')],
  }],
  # Extra data we want in our output directory
  data_files=[
      ('html', glob.glob('html/*.html')),
      ('images', glob.glob('images/*')),
      ('help', glob.glob('help/*')),
  ],
  )
