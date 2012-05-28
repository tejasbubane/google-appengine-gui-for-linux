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

"""Convenience wrapper for starting the launcher."""

import sys

try:
  import wx
except ImportError, inst:
  print >>sys.stderr, 'wxPython is not available'
  sys.exit(1)

REQUIRED_WX_VERSION = (2,8)
CURRENT_WX_VERSION = wx.VERSION[:2]
if CURRENT_WX_VERSION != REQUIRED_WX_VERSION:
  print >>sys.stderr, ('wxPython version incorrect; is %d.%d, must be %d.%d' %
                       (CURRENT_WX_VERSION + REQUIRED_WX_VERSION))
  sys.exit(2)

import launcher

if __name__ == '__main__':
  # For Linux/Mac, redirect=False gives me a stack trace on the command line.
  # TODO(jrg): remove when not debugging
  redirect = False
  
  app = launcher.App(redirect=redirect)
  app.MainLoop()
