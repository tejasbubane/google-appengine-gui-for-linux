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

"""Unit test for dialog_controller_base.py."""


import unittest
import mox
import wx
import launcher


class DialogControllerBaseTest(unittest.TestCase):

  def Bind(self, event, closure, button):
    """Fake Bind() call since we use ourself as a fake wx.Dialog."""
    self.buttons.append(button)

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()
    self.buttons = []

  def testEndModalClosure(self):
    project = launcher.Project('path', 9000)
    sc = launcher.SettingsController(project)
    for code in (wx.ID_OK, wx.ID_CANCEL):
      dialog_mock = mox.MockObject(wx.Dialog)
      dialog_mock.EndModal(code)
      mox.Replay(dialog_mock)
      closure = sc.EndModalClosure(dialog_mock, code)
      closure(None)
      mox.Verify(dialog_mock)

  def testBind(self):
    d = launcher.DialogControllerBase()
    d.dialog = self  # we are a mock dialog
    self.update_button = 1
    self.cancel_button = 2
    d.MakeBindingsOKCancel()
    self.assertEqual(sorted(self.buttons), [1, 2])
    self.buttons = []
    del(self.update_button)
    self.ok_button = 10
    d.MakeBindingsOKCancel()
    self.assertEqual(sorted(self.buttons), [2, 10])
    d.dialog = None  # so Destroy() isn't called


if __name__ == '__main__':
  unittest.main()
