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

"""Unittests for addexisting_controller.py."""


import unittest
import mox
import wx
from wxgladegen import project_dialogs
import launcher


class AddExistingControllerTest(unittest.TestCase):
  """Unit test case for AddExistingController."""

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()

  def testInit(self):
    ae = launcher.AddExistingController()
    self.assertTrue(ae.dialog)
    self.assertNotEqual(wx.ID_OK, ae._dialog_return_value)

  def testGetSet(self):
    ae = launcher.AddExistingController()
    ae.SetPath('hi mom')
    for num in (10, 1024, 8000, 9100, 7999):
      ae.SetPort(num)
      self.assertEqual(num, int(ae.GetPort()))
    self.assertEqual('hi mom', ae.GetPath())
    for path in ('foo', '/tmp/zazzimataz', 'c:\\win\\path', ''):
      ae.SetPath(path)
      self.assertEqual(path, ae.GetPath())
    ae.SetPath(None)
    self.assertEqual('', ae.GetPath())

  def testShowModal(self):
    # 9 lines in testShowModal() to test 2 lines of ShowModal() seems excessive.
    ae = launcher.AddExistingController()
    for wx_dialog_return_value in (wx.ID_OK, wx.ID_CANCEL, wx.ID_OK):
      dialog_mock = mox.MockObject(project_dialogs.AddExistingProjectDialog)
      dialog_mock.ShowModal().AndReturn(wx_dialog_return_value)
      mox.Replay(dialog_mock)
      ae.dialog = dialog_mock
      rtn = ae.ShowModal()
      self.assertEqual(wx_dialog_return_value, rtn)
      self.assertEqual(ae._dialog_return_value, rtn)
      mox.Verify(dialog_mock)

  def testSanityCheckPathPort(self):
    failures = [0]
    def MarkFailure(msg, capt):
      failures[0] += 1
    ae = launcher.AddExistingController()
    ae.FailureMessage = MarkFailure
    self.assertFalse(ae._SanityCheckPort('hi'))
    self.assertFalse(ae._SanityCheckPort(52))
    self.assertTrue(ae._SanityCheckPort(8000))
    self.assertTrue(ae._SanityCheckPort(8123))
    self.assertFalse(ae._SanityCheckPath(None))
    self.assertFalse(ae._SanityCheckPath('/fmofmfomfoff'))
    failures = [0]
    self.assertTrue(ae._SanityCheckPath('.'))
    self.assertEqual(1, failures[0])  # since no app.yaml

  def testProject(self):
    ae = launcher.AddExistingController()
    def IgnoreFailure(msg, capt):
      pass
    ae.FailureMessage = IgnoreFailure
    self.assertFalse(ae.Project())
    ae._dialog_return_value = wx.ID_OK
    ae.SetPath('hi mom')
    ae.SetPort('hi mom')
    self.assertFalse(ae.Project())
    ae.SetPath('.')
    ae.SetPort(8010)
    self.assertTrue(ae.Project())


if __name__ == '__main__':
  unittest.main()
