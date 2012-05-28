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

"""Unit test for deploy_controller.py"""

import time
import unittest
import wx
from wxgladegen import auth_dialog
import launcher


class DeployControllerTest(unittest.TestCase):

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()

    class EmptyPref(object):
      def Get(self, name):
        return None
    self.emptypref = EmptyPref()

  def testInit(self):
    runtime = launcher.Runtime()
    preferences = launcher.Preferences()
    projects = ['hi', 'mom']
    dialog = auth_dialog.AuthDialog(None)
    d = launcher.DeployController(runtime, preferences, projects, dialog)
    self.assertEqual(dialog, d.dialog)
    d = launcher.DeployController(runtime, preferences, projects)
    self.assertTrue(d.dialog)

  def testInitiateDeployment(self):
    deployed = [False]
    def FakeDoDeploy():
      deployed[0] = True
    d = launcher.DeployController(None, None, None)
    d._DoDeploy = FakeDoDeploy
    d._GetNameAndPassword = (lambda: wx.ID_CANCEL)
    self.assertEqual(wx.ID_CANCEL, d.InitiateDeployment())
    self.assertFalse(deployed[0])
    d._GetNameAndPassword = (lambda: wx.ID_OK)
    self.assertEqual(wx.ID_OK, d.InitiateDeployment())
    self.assertTrue(deployed[0])

  def testGetNameAndPassword(self):
    d = launcher.DeployController(None, self.emptypref, None)
    d.dialog.ShowModal = (lambda: wx.ID_CANCEL)
    self.assertEqual(wx.ID_CANCEL, d._GetNameAndPassword())
    d.dialog.ShowModal = (lambda: wx.ID_OK)
    d.dialog.name_text_ctrl.SetValue('fred')
    d.dialog.password_text_ctrl.SetValue('fredz_seekret_passwerd_shh')
    self.assertEqual(wx.ID_OK, d._GetNameAndPassword())
    self.assertEqual('fred', d._authname)
    self.assertEqual('fredz_seekret_passwerd_shh', d._password)

  def testTextFrameForProject(self):
    project = launcher.Project('path', 8000, 'project_name')
    d = launcher.DeployController(None, None, [project])
    tf = d._TextFrameForProject(project)
    self.assertTrue('project_name' in tf.GetTitle())
    self.assertTrue(tf.IsShown())

  def testTaskThreadForProject(self):
    project = launcher.Project('path', 8000, 'project_name')
    d = launcher.DeployController(launcher.Runtime(), launcher.Preferences(),
                                  [project])
    d._name = 'fred'
    d._password = 'himom'
    tt = d._TaskThreadForProject(project)
    self.assertFalse(tt.isAlive())
    # confirm stdin works.  Use python so we don't need cygwin.
    # Print out the 'Running application' string so that
    # taskthread will know to transition from WillStart to DidStart.
    script = ('import sys; print "Running application http://x:5"; '
              'print sys.stdin.read().strip()')
    cat_cmd = [sys.executable, '-c', script]
    tt = d._TaskThreadForProject(project, cat_cmd)
    output = ['']
    def collect(line, date=True):
      output[0] += line
    tt.LogOutput = collect
    starting = [0]
    started = [0]
    lock = threading.Lock()
    def _TaskWillStart():
      starting[0] = time.time()
    def _TaskDidStart():
      started[0] = time.time()
    def _TaskDidStop(code):
      lock.release()
    tt._TaskWillStart = _TaskWillStart
    tt._TaskDidStart = _TaskDidStart
    tt._TaskDidStop = _TaskDidStop
    lock.acquire()
    tt.start()
    lock.acquire()  # blocks until _TaskDidStop() releases it
    lock.release()
    self.assertNotEqual(0, starting[0])
    self.assertNotEqual(0, started[0])
    # Make sure the 'started' happens after 'starting'
    self.assertTrue(started > starting)
    self.assertTrue('himom' in output[0])

  def testDoDeploy(self):
    project = launcher.Project('path', 8000, 'project_name')
    d = launcher.DeployController(None, None, [project])
    d._password = 'shh'
    self.assertFalse(d._DoDeploy()) # no name
    d._password = None
    d._authname = 'joe'
    self.assertFalse(d._DoDeploy()) # no password

    projects = [launcher.Project('path', 8000+x, 'name') for x in range(3)]
    started = [0]
    for p in projects:
      def dummy_start():
        started[0] += 1
      p.start = dummy_start
    d = launcher.DeployController(None, None, projects)
    d._authname = 'fred'
    d._password = 'shh'
    d._TextFrameForProject = (lambda x: x)
    d._TaskThreadForProject = (lambda x: x)
    self.assertTrue(d._DoDeploy())
    self.assertEqual(3, len(d._text_frames))
    self.assertEqual(3, len(d._task_threads))
    for p in projects:
      self.assertEqual(3, started[0])

    # We're already setup for testing, so while we're here,
    # let's test _TaskDidStop and DisplayProjectOutput
    didit = [False]
    def append_text(line):
      didit[0] = True
    projects[0].AppendText = append_text
    d._TaskDidStop(projects[0])  # appends one last line of text
    self.assertTrue(didit[0])
    self.assertEqual(2, len(d._text_frames))
    self.assertEqual(2, len(d._task_threads))

  def testDeployServer(self):

    class MockPref(object):
      def __init__(self, pref=None):
        self.pref = pref
      def Get(self, name):
        if name == launcher.Preferences.PREF_DEPLOY_SERVER:
          return self.pref
        return None

    class MockText(object):
      def __init__(self):
        self.text = None
      def SetLabel(self, text):
        self.text = text

    project = launcher.Project('path', 8000, 'project_name')
    mockpref = MockPref()
    mocktext = MockText()
    d = launcher.DeployController(None, mockpref, [project])
    d._AddDeployServerToTextField(mocktext)
    self.assertFalse(mocktext.text)

    mockpref = MockPref('hi dave')
    d = launcher.DeployController(None, mockpref, [project])
    d._AddDeployServerToTextField(mocktext)
    self.assertTrue('dave' in mocktext.text)


if __name__ == '__main__':
  unittest.main()
