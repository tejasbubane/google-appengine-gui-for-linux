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

"""Unittests for log_console.py"""

import unittest
import wx
import launcher


class LogConsoleTest(unittest.TestCase):

  def ConfirmedShow(self, doshow):
    """Dropped into the Console so we can insure Show(False) has been called."""
    if doshow == False:
      self.did_hide = True

  def ConfirmedDestroy(self):
    """Dropped into the Console so we can insure Destroy() has been called."""
    self.did_destroy = True

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()

  def testBasics(self):
    project = launcher.Project('path', 8000, 'name')
    lc = launcher.LogConsole(project)
    self.assertEqual(project, lc.project)

  def testCloseHandler(self):
    """Test our close handler (if not force, hide window and save for later)"""
    project = launcher.Project('path', 8000, 'name')
    lc = launcher.LogConsole(project)
    self.did_hide = False
    self.did_destroy = False
    orig_show = lc.Show
    orig_destroy = lc.Destroy
    # Override some methods so we can track behavior
    lc.Show = self.ConfirmedShow
    lc.Destroy = self.ConfirmedDestroy
    # Call our wx.EVT_CLOSE handler; CAN be veto'ed
    lc.Close(force=False)
    self.assertTrue(self.did_hide)
    self.assertFalse(self.did_destroy)
    self.did_hide = False
    self.did_destroy = False
    # Call our wx.EVT_CLOSE handler; CANNOT be veto'ed
    lc.Close(force=True)
    self.assertFalse(self.did_hide)
    self.assertTrue(self.did_destroy)
    # Restore original methods
    lc.Show = orig_show
    lc.Destroy = orig_destroy


if __name__ == "__main__":
  unittest.main()
