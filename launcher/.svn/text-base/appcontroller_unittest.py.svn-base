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
"""Unittests for appcontroller.py"""

import unittest
import mox
import shutil
import tempfile
import wx
import launcher


class FakeFrame(object):
  def RefreshView(self, projects):
    pass

class FakeTable(object):
  def __init__(self):
    self._projects = None
  def UniquePort(self):
    return 8123
  def AddProject(self, project):
    pass

class NoAskController(launcher.AppController):
  """An AppController that doesn't ask; it has a set project to return."""
  def __init__(self, app, project):
    super(NoAskController, self).__init__(app)
    self._hard_coded_project = project
    self.SetModelsViews(frame=FakeFrame(), table=FakeTable())
    self._path = None

  def _AskForProject(self, controller, path=None):
    self._path = path
    return self._hard_coded_project


class AppControllerTest(unittest.TestCase):

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()

  def Projects(self, n):
    """Convenience routine for creating unique projects.

    Args:
      n: number of unique projects

    Returns:
      A list of N unique projects.
    """
    projects = []
    for i in range(n):
      name = '/tmp/himom-%d' % i
      projects.append(launcher.Project(name, 8000+i))
    return projects

  def testInitAndConfigure(self):
    c = launcher.AppController(self.app)
    self.assertFalse(c._frame)
    self.assertFalse(c._table)
    table = 1
    frame = 2
    c.SetModelsViews(frame=frame, table=None)
    self.assertTrue(c._frame == frame)
    c.SetModelsViews(frame=None, table=table)
    self.assertTrue(c._table == table)
    c.SetModelsViews(frame=table, table=frame)
    self.assertTrue(c._frame == table)
    self.assertTrue(c._table == frame)

  def testAdd(self):
    """Tests both Add() and AddNew()."""
    for attr in ('Add', 'AddNew'):
      p = launcher.Project('/tmp/himom', 8123)
      # Avoid UI with a NoAskController
      controller = NoAskController(self.app, p)
      # Mock table to confirm AddProject() gets called
      table_mock = mox.MockObject(launcher.MainTable)
      table_mock.AddProject(p)
      table_mock._projects = None
      mox.Replay(table_mock)
      controller.SetModelsViews(table=table_mock)
      # UI should be noop, and table.AddProject() should be called in here
      getattr(controller, attr)(None)
      mox.Verify(table_mock)
    # Make sure the path makes it to the controller.
    c = NoAskController(self.app, None)
    c.Add(None, '/Path/To/Oblivion')
    self.assertEqual('/Path/To/Oblivion', c._path)

  def testRemove(self):
    """Test Remove with both single and multiple projects."""
    # Simulate with both positive and negative responses.
    # These functions will replace  launcher.Controller_ConfirmRemove().
    confirm_functions = (lambda a, b: True, lambda a, b: False)
    for confirm_function in confirm_functions:
      plists = (self.Projects(1), self.Projects(4))
      for projectlist in plists:
        frame_mock = mox.MockObject(launcher.MainFrame)
        frame_mock.SelectedProjects().AndReturn(projectlist)
        table_mock = mox.MockObject(launcher.MainTable)
        table_mock._projects = None
        # Only if _ConfirmRemove() will return True do we tell our
        # mock to expect deletes to happen (RemoveProject() calls).
        if confirm_function(0,0):
          for p in projectlist:
            table_mock.RemoveProject(p).InAnyOrder()
          frame_mock.UnselectAll()
          frame_mock.RefreshView(None)
        mox.Replay(frame_mock)
        mox.Replay(table_mock)
        controller = launcher.AppController(self.app)
        controller._ConfirmRemove = confirm_function
        controller.SetModelsViews(frame=frame_mock, table=table_mock)
        controller.Remove(None)
        mox.Verify(frame_mock)

  def testSettings(self):
    ac = launcher.AppController(self.app)
    failures = [0]
    def failure_accum(a, b):
      failures[0] += 1
    ac._FailureMessage = failure_accum
    # First make sure we choke if !=1 project is selected
    for projectlist in ((), (1, 2, 4)):
      failures = [0]
      frame_mock = mox.MockObject(launcher.MainFrame)
      frame_mock.SelectedProjects().AndReturn(projectlist)
      mox.Replay(frame_mock)
      ac.SetModelsViews(frame=frame_mock)
      ac.Settings(self, None)
      mox.Verify(frame_mock)
      self.assertEqual(1, failures[0])
    # Now test things look fine with 1 project.
    frame_mock = mox.MockObject(launcher.MainFrame)
    frame_mock.SelectedProjects().AndReturn((1,))
    frame_mock.RefreshView(None)
    mox.Replay(frame_mock)
    table_mock = mox.MockObject(launcher.MainTable)
    table_mock.SaveProjects()
    table_mock._projects = None
    mox.Replay(table_mock)
    ac.SetModelsViews(frame=frame_mock, table=table_mock)
    controller_mock = mox.MockObject(launcher.SettingsController)
    controller_mock.ShowModal().AndReturn(wx.ID_OK)
    mox.Replay(controller_mock)
    ac.Settings(None, settings_controller=controller_mock)
    mox.Verify(frame_mock)
    mox.Verify(table_mock)
    mox.Verify(controller_mock)

  def testOnPreferences(self):
    ac = launcher.AppController(self.app)
    pref_controller_mock = mox.MockObject(launcher.PrefController)
    pref_controller_mock.ShowModal()
    mox.Replay(pref_controller_mock)
    ac.OnPreferences(None, pref_controller_mock)
    mox.Verify(pref_controller_mock)

  def testOnAbout(self):
    # I tried to combine this with the above and a parameterized
    # helper, but (with extra doc et al) it ended up being larger and
    # just increasing complexity.
    ac = launcher.AppController(self.app)
    ab_controller_mock = mox.MockObject(launcher.AboutBoxController)
    ab_controller_mock.ShowModal()
    mox.Replay(ab_controller_mock)
    ac.OnAbout(None, ab_controller_mock)
    mox.Verify(ab_controller_mock)

  def testInstallDemoByName(self):
    # Create a demo source
    sourcedir = tempfile.mkdtemp()
    demo = os.path.join(sourcedir, 'sooper-dooper-demo')
    os.mkdir(demo)
    yaml = os.path.join(demo, 'app.yaml')
    f = open(yaml, 'w')
    f.write('hi mom\n')
    f.close()
    # Create a demo dest dir
    destdir = tempfile.mkdtemp()
    # Now copy a demo.
    ac = NoAskController(self.app, launcher.Project('hi', 8000))
    ac.InstallDemoByName(demo, destdir, False)
    self.assertTrue(os.path.basename(demo) in os.listdir(destdir))
    for copied_demo in os.listdir(destdir):
      self.assertTrue(os.path.exists(os.path.join(destdir, copied_demo,
                                                  'app.yaml')))
    # Now copy another, trying to conflict.
    ac.InstallDemoByName(demo, destdir, False)
    self.assertEqual(2, len(os.listdir(destdir)))
    for copied_demo in os.listdir(destdir):
      self.assertTrue(os.path.exists(os.path.join(destdir, copied_demo,
                                                  'app.yaml')))
    # Now for a 3rd to test out counter.
    ac.InstallDemoByName(demo, destdir, False)
    self.assertEqual(3, len(os.listdir(destdir)))
    # Finally, clean up.
    shutil.rmtree(sourcedir)
    shutil.rmtree(destdir)


if __name__ == "__main__":
  unittest.main()
