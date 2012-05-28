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

"""Unittests for preferenceview.py."""

import unittest
import mox
import wx
import launcher

class PreferenceViewTest(unittest.TestCase):

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()

  def testBasics(self):
    p = launcher.PreferenceView()
    self.assertTrue(p.PreferenceCount() == 0)
    self.assertFalse(p.Get('foo'))
    self.assertFalse(p.Get('bar'))
    p.Append('foo')
    p.Append('bar', value='himom')
    self.assertEqual(2, p.PreferenceCount())
    self.assertFalse(p.Get('foo'))
    self.assertEqual('himom', p.Get('bar'))
    p.Append('baz', value='baz', default='whee')
    self.assertEqual(3, p.PreferenceCount())
    self.assertEqual('baz', p.Get('baz'))

  def testSelectors(self):
    p = launcher.PreferenceView()
    self.assertTrue(p.PreferenceCount() == 0)
    p.Append('oz_file', file_selector=True)
    self.assertTrue(p.FindWindowByName('oz_file'))
    self.assertEqual('file', p.selectors['oz_file'])
    p.Append('oz_dir', dir_selector=True)
    self.assertTrue(p.FindWindowByName('oz_dir'))
    self.assertEqual('directory', p.selectors['oz_dir'])

  def ReturnStringMethod(self, str):
    """Return a method that returns the input string."""
    def rsfunc(self):
      return str
    return rsfunc

  def commonTestButton(self, id, path, newval):
    """Common button test routine.

    Args:
      id: the wx.ID_* we want sent by the dialog
      path: the GetPath() we want returned by the dialog.
        If none, do not expect it.
      newval: what we expect our pref to be set to when done
    """
    p = launcher.PreferenceView()
    mymox = mox.Mox()
    dialog = mymox.CreateMock(wx.FileDialog)
    dialog.ShowModal().AndReturn(id)
    if path:
      dialog.GetPath().AndReturn(path)
    mymox.ReplayAll()
    p._NameFromEvent = self.ReturnStringMethod('python')
    p.Append('python')
    p._OnFileDirectoryButtonCommon(None, dialog)
    mymox.VerifyAll()
    if not newval:
      self.assertFalse(p.Get('python'))
    else:
      self.assertTrue(p.Get('python') == newval)

  def testButtonOK(self):
    self.commonTestButton(wx.ID_OK, 'superman', 'superman')

  def testButtonCancel(self):
    self.commonTestButton(wx.ID_CANCEL, None, None)


if __name__ == '__main__':
  unittest.main()
