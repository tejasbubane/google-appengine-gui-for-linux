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

"""Unittests for taskcontroller.py"""

import unittest
import wx
import mox
import launcher


class FakeAppController(object):
  def RefreshMainView(self):
    pass

class FakeDevAppServerTaskThread(launcher.DevAppServerTaskThread):
  """Fake task thread to aid in testing.

  We stub out a few things here. Painful to use a mock.
  """

  def __init__(self, controller, project, cmd):
    super(FakeDevAppServerTaskThread, self).__init__(controller, project, cmd)
    # use int instead of bool so we can spot redundant runs
    self.runval = 0

  def start(self):
    self.runval += 1

  def stop(self):
    self.runval -= 1


class TaskControllerTest(unittest.TestCase):

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()
    self.threads = []
    self.browsed = []

  def testInit(self):
    """Test basic initialization of a TaskController."""
    tc = launcher.TaskController(FakeAppController())
    self.assertFalse(tc._frame)
    tc.SetModelsViews(frame=102)
    self.assertEqual(tc._frame, 102)

  def Projects(self, n):
    """Return a list of N unique Projects.

    Args:
      n: the number of unique Projects we will generate
    Returns:
      A list of unique Projects
    """
    projects = []
    for i in range(n):
      name = '/tmp/himom-%d' % i
      projects.append(launcher.Project(name, i+8000))
    return projects


  def _CreateTaskThreadForProject(self, project, cmd):
    """Override of taskcontroller method to return a fake thread.
    Call self.ConfirmThreads() when done.
    """
    thread = FakeDevAppServerTaskThread(None, project, cmd)
    self.threads.append(thread)
    return thread

  def ConfirmThreads(self, runval):
    """Confirm all our thread mocks are happy.
    Confirm all their run states are as expected.

    Args:
      runval: the thread run state we expect for all threads
    """
    for thread in self.threads:
      self.assertEqual(thread.runval, runval)

  def doTestRunStateChanges(self, initial_runstate, end_runstate, attrname,
                            do_selected=True):
    """test calling attrname with both a single and multi-selection of projects.
    Sets initial run state of the projects, and confirms it gets switched to
    end_runstate.

    Args:
      initial_runstate: the initial run state of the Projects
      end_runstate: the end run state of the Projects after the op
      attrname: call this attribute for each project
      do_selected: if True, do mock a SelectedProjects() call.
    """
    plists = (self.Projects(1), self.Projects(4))
    for projectlist in plists:
      for p in projectlist:
        p.runstate = initial_runstate
      tc = launcher.TaskController(FakeAppController())
      tc.SetModelsViews(runtime=launcher.Runtime())
      stateop = getattr(tc, attrname)
      self.assertTrue(callable(stateop))
      # Override thread creation; don't want real tasks running
      tc._CreateTaskThreadForProject = self._CreateTaskThreadForProject
      # Mock out "selected projects" of the frame to return projectlist
      frame_mock = mox.MockObject(launcher.MainFrame)
      if do_selected:
        frame_mock.SelectedProjects().AndReturn(projectlist)
      mox.Replay(frame_mock)
      tc.SetModelsViews(frame=frame_mock)
      # Finally, call the method we are testing, and verify
      stateop(None)
      mox.Verify(frame_mock)
      self.ConfirmThreads(end_runstate)
      # re-run our op and make sure no threads are modified/added/removed
      tmlen = len(self.threads)
      mox.Reset(frame_mock)
      if do_selected:
        frame_mock.SelectedProjects().AndReturn(projectlist)
      mox.Replay(frame_mock)
      stateop(None)
      mox.Verify(frame_mock)
      self.assertEqual(tmlen, len(self.threads))
      self.ConfirmThreads(end_runstate)

  def testRun(self):
    self.doTestRunStateChanges(0, 1, 'Run')

  def testStop(self):
    self.doTestRunStateChanges(1, 0, 'Stop')

  def testStopAll(self):
    self.doTestRunStateChanges(1, 0, 'StopAll', do_selected=False)

  def testRunStrict(self):
    self.doTestRunStateChanges(0, 1, 'RunStrict')
    # Also confirm we find the extra flag
    flagslist = [None]
    def SaveFlags(extra_flags=[]):
      flagslist[0] = extra_flags
    tc = launcher.TaskController(FakeAppController())
    tc._GenericRun = SaveFlags
    tc.Run(None)
    self.assertFalse('--require_indexes' in flagslist[0])
    flagslist = [None]
    tc.RunStrict(None)
    self.assertTrue('--require_indexes' in flagslist[0])

  def _FakeBrowseProject(self, project):
    """Fake browse function."""
    url = 'http://localhost:%d' % project.port
    self.browsed.append(url)

  def testBrowse(self):
    projects = self.Projects(5)
    # projects 0 and 2 are STOP by default
    for i in (1,3,4):
      projects[i].runstate = launcher.Project.STATE_RUN
    tc = launcher.TaskController(FakeAppController())
    # We don't really care about the mock, other than as a convenient
    # way to override one method of the frame.
    frame_mock = mox.MockObject(launcher.MainFrame)
    frame_mock.SelectedProjects().AndReturn(projects)
    mox.Replay(frame_mock)
    tc.SetModelsViews(frame=frame_mock)
    tc._BrowseProject = self._FakeBrowseProject
    tc.Browse(None)
    # Make sure only the running projects were browsed
    for i in (0,2):
      self.assertFalse(('http://localhost:%d' % (i+8000)) in self.browsed)
    for i in (1,3,4):
      self.assertTrue(('http://localhost:%d' % (i+8000)) in self.browsed)

  def _FindOrCreateConsoleLogs(self, project):
    """Override of TaskController's method to return a mock.

    For use with testLogs, below.
    """
    console = mox.MockObject(launcher.LogConsole)
    console.DisplayAndBringToFront()
    self.consoles.append(console)
    mox.Replay(console)
    return console

  def testLogs(self):
    self.consoles = []
    projectlist = self.Projects(17)
    tc = launcher.TaskController(FakeAppController())
    frame_mock = mox.MockObject(launcher.MainFrame)
    frame_mock.SelectedProjects().AndReturn(projectlist)
    mox.Replay(frame_mock)
    tc.SetModelsViews(frame=frame_mock)
    tc._FindOrCreateConsole = self._FindOrCreateConsoleLogs
    tc.Logs(None)
    mox.Verify(frame_mock)
    for c in self.consoles:
      mox.Verify(c)

  def _FindThreadForProject(self, project):
    """Override of taskcontroller to make sure it is called."""
    self.assertEqual(project, self.to_be_found)
    self.looked_for = True
    return None

  def testRunStateChanged(self):
    projects = self.Projects(2)
    # 0 is STOP so it'll be looked for
    self.to_be_found = projects[0]
    self.looked_for = False
    projects[1].runstate = launcher.Project.STATE_RUN
    frame_mock = mox.MockObject(launcher.MainFrame)
    tc = launcher.TaskController(FakeAppController())
    tc._FindThreadForProject = self._FindThreadForProject
    tc.SetModelsViews(frame=frame_mock)
    mox.Replay(frame_mock)
    for project in projects:
      tc.RunStateChanged(project)
    mox.Verify(frame_mock)
    self.assertTrue(self.looked_for)

  def _FindOrCreateConsoleDPO(self, project):
    """Override of TaskController's method to return a mock.

    For use with testDisplayProjectOutput, below.
    """
    self.assertTrue(project == 'momproject')
    self.console = mox.MockObject(launcher.LogConsole)
    self.console.AppendText('hi')
    mox.Replay(self.console)
    return self.console

  def testDisplayProjectOutput(self):
    """Test of TaskController's DisplayProjectOutput."""
    tc = launcher.TaskController(FakeAppController())
    tc._FindOrCreateConsole = self._FindOrCreateConsoleDPO
    tc.DisplayProjectOutput('momproject', 'hi')
    mox.Verify(self.console)

  def testSDKConsole(self):
    projects = self.Projects(5)
    tc = launcher.TaskController(FakeAppController())
    frame_mock = mox.MockObject(launcher.MainFrame)
    frame_mock.SelectedProjects().MultipleTimes().AndReturn(projects)
    mox.Replay(frame_mock)
    tc.SetModelsViews(frame=frame_mock)
    browsed_projects = []
    def FakeBrowse(project):
      browsed_projects.append(project)
    tc._BrowseAdminConsoleForProject = FakeBrowse
    # none are running so we expect no browsing
    tc.SdkConsole(None)
    self.assertFalse(browsed_projects)
    for i in (1,3,4):
      projects[i].runstate = launcher.Project.STATE_RUN
    tc.SdkConsole(None)
    self.assertEqual(3, len(browsed_projects))
    mox.Verify(frame_mock)

  def testDeploy(self):
    projects = self.Projects(5)
    tc = launcher.TaskController(FakeAppController())
    frame_mock = mox.MockObject(launcher.MainFrame)
    frame_mock.SelectedProjects().MultipleTimes().AndReturn(projects)
    mox.Replay(frame_mock)
    deploy_controller = mox.MockObject(launcher.DeployController)
    deploy_controller.InitiateDeployment()
    mox.Replay(deploy_controller)
    tc.SetModelsViews(frame=frame_mock)
    tc.Deploy(None, deploy_controller)
    mox.Verify(deploy_controller)
    mox.Verify(frame_mock)

  def testDashboard(self):
    projects = self.Projects(5)
    tc = launcher.TaskController(FakeAppController())
    frame_mock = mox.MockObject(launcher.MainFrame)
    frame_mock.SelectedProjects().MultipleTimes().AndReturn(projects)
    mox.Replay(frame_mock)
    tc.SetModelsViews(frame=frame_mock)
    browsed = []
    def Browse(project):
      browsed.append(project)
    tc._BrowseDashboardForProject = Browse
    tc.Dashboard(None)
    self.assertEqual(sorted(projects), sorted(browsed))
    mox.Verify(frame_mock)


if __name__ == '__main__':
  unittest.main()
