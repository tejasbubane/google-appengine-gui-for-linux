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

"""Unit test for dev_appserver_task_thread.py"""


import unittest
import wx
import launcher


class DevAppServerTaskThreadTest(unittest.TestCase):

  def setUp(self):
    # Some tests wander into wx, so we need a wx.App cranked up.
    self.app = wx.PySimpleApp()

  def RunStateChanged(self, project):
    """We use ourself as a fake controller for convenience."""
    self.project_changed = project

  def FakeCallAfter(self, callable, project):
    callable(project)

  def testBasics(self):
    datt = launcher.DevAppServerTaskThread(self, self, None)
    # replace wx.CallAfter so we don't have to run an event loop
    orig_callafter = wx.CallAfter
    wx.CallAfter = self.FakeCallAfter

    self.project_changed = None
    self.runstate = launcher.Project.STATE_STOP
    datt._TaskWillStart()
    self.assertEqual(self.project_changed, self)
    self.assertEqual(self.runstate, launcher.Project.STATE_STARTING)

    self.project_changed = None
    self.runstate = None
    datt._TaskDidStart()
    self.assertEqual(self.project_changed, self)
    self.assertEqual(self.runstate, launcher.Project.STATE_RUN)

    self.project_changed = None
    self.runstate = None
    datt._TaskDidStop(42)  # 42 falls into the failure zone.
    self.assertEqual(self.project_changed, self)
    self.assertEqual(self.runstate, launcher.Project.STATE_DIED)

    # Exercise a successful result code.  Zero is a success for all platforms.
    self.project_changed = None
    self.runstate = None
    datt._TaskDidStop(0)
    self.assertEqual(self.project_changed, self)
    self.assertEqual(self.runstate, launcher.Project.STATE_STOP)

    # Exercise some unsuccessful result codes
    for code in (-42, 1, 100):
      self.project_changed = None
      self.runstate = None
      datt._TaskDidStop(code)
      self.assertEqual(self.project_changed, self)
      self.assertEqual(self.runstate, launcher.Project.STATE_DIED)

    wx.CallAfter = orig_callafter


if __name__ == '__main__':
  unittest.main()
