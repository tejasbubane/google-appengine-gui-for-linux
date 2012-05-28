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
"""Unit test for settings_controller.py."""

import unittest
import mox
import wx
from wxgladegen import project_dialogs
import launcher


class SettingsControllerTest(unittest.TestCase):

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()

  def testShowModal(self):
    project = launcher.Project('path', 9000)
    for (wx_rtn, updated_calls) in ((wx.ID_OK, 1), (wx.ID_CANCEL, 0)):
      sc = launcher.SettingsController(project)
      settings_dialog = project_dialogs.ProjectSettingsDialog
      dialog_mock = mox.MockObject(settings_dialog)
      dialog_mock.ShowModal().AndReturn(wx_rtn)
      mox.Replay(dialog_mock)
      sc.dialog = dialog_mock
      actual_updated = [0]
      def plusone():
        """Must use mutable to modify var in enclosing scope."""
        actual_updated[0] += 1
      sc._UpdateProject = plusone
      rtn = sc.ShowModal()
      self.assertEqual(wx_rtn, rtn)
      mox.Verify(dialog_mock)
      self.assertEqual(updated_calls, actual_updated[0])
      # SettingsController needs to Destroy() its dialog.
      # That is done in SettingsController's __del__.
      # But that's past the mox.Verify(), so we can't expect it.
      # We can, however, make sure it doesn't cause mox
      # to yell.
      sc.dialog = None

  def testUpdateProject(self):
    project = launcher.Project('path', 9001)
    sc = launcher.SettingsController(project)
    # Basic change:
    # First a port...
    sc.dialog.app_port_text_ctrl.SetValue(str(1008))
    sc._UpdateProject()
    self.assertEqual(1008, project.port)
    # Then a flag.
    sc.dialog.full_flag_list_text_ctrl.SetValue('--bozo-assault')
    sc._UpdateProject()
    self.assertTrue('--bozo-assault' in project.flags)
    # Deny a change if it's running
    failures = [0]
    def plusone(arg1, arg2):
        """Must use mutable to modify var in enclosing scope."""
        failures[0] += 1
    sc.FailureMessage = plusone
    # First change the port...
    oldport = project.port
    sc.dialog.app_port_text_ctrl.SetValue(str(5555))
    project.runstate = launcher.Project.STATE_RUN
    sc._UpdateProject()
    self.assertEqual(1, failures[0])
    failures[0] = 0
    # Restore, then change the flags
    sc.dialog.app_port_text_ctrl.SetValue(str(oldport))
    sc.dialog.full_flag_list_text_ctrl.SetValue('--anti-clown-spray')
    sc._UpdateProject()
    self.assertEqual(1, failures[0])

  def testParseFlags(self):
    project = launcher.Project('path', 9000)
    sc = launcher.SettingsController(project)
    flagtests = { '': [],
                  '\n\n\n\n\n\n--keyboard': ['--keyboard'],
                  '-d': ['-d'],
                  '--debug': ['--debug'],
                  '-f --foo': ['-f', '--foo'],
                  '--foo -f': ['--foo', '-f'],
                  '  --zoo\n--path=hi mom  -d --fred=hi mom --zoo':
                  ['--zoo', '--path=hi mom', '-d',  '--fred=hi mom', '--zoo'] }
    for key in flagtests:
      flaglist = sc._ParseFlags(key)
      self.assertEqual(flagtests[key], flaglist)


if __name__ == '__main__':
  unittest.main()
