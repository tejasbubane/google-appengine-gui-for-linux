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
"""Unittests for taskthread.py"""

import unittest
import sys
import time
import wx
import launcher


class FakeAppController(object):
  def RefreshMainView(self):
    pass

class TaskThreadTest(unittest.TestCase):

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()

  def doTestThreadRun(self, killit=False):
    """Run a command, watch for state change.
    Optionally kill it to speed up death.
    """
    controller = launcher.TaskController(FakeAppController())
    project = launcher.Project('himom', 8000)
    secs = 3
    if killit:
      # If in killit mode, make sure it'll last longer than us so we
      # don't confuse kill with runout
      secs = 20
    # Start a task ripe for the killing.
    command = [sys.executable, '-c', 'import time; time.sleep(%d)' % secs]
    tt = launcher.TaskThread(controller, project, command)
    tt.start()
    # TODO(jrg): is this a reasonable chance?
    for i in range(20):
      time.sleep(0.25)
      if tt.isAlive():
        break
    self.assertTrue(tt.isAlive())
    if killit:
      tt.stop()
    for i in range(20):
      time.sleep(0.25)
      if not tt.isAlive():
        break
    self.assertFalse(tt.isAlive())
    pass

  def testRunOut(self):
    self.doTestThreadRun(killit=False)

  def testKilled(self):
    self.doTestThreadRun(killit=True)

  def testLaunchLogLineCompleted(self):
    tt = launcher.TaskThread(self, None, None)
    line = ('INFO     2009-04-08 15:36:23,888 dev_appserver_main.py] Running '
            'application TheDen on port 8015: http://localhost:8015')
    self.assertTrue(tt._IsLaunchCompletedLogLine(line))
    line = ('INFO     2009-04-08 15:36:23,888 dev_appserver_main.py] Running '
            'application greeblebork on port 8000: '
            'http://oop.ack.blarg.co.ukt:8000')
    self.assertTrue(tt._IsLaunchCompletedLogLine(line))
    line = 'Running application http://x:5'
    self.assertTrue(tt._IsLaunchCompletedLogLine(line))
    # Take some output from a real dev_appserver and make sure it doesn't match.
    line = 'socket.error: (48, \'Address already in use\')'
    self.assertFalse(tt._IsLaunchCompletedLogLine(line))
    line = ('WARNING  2009-04-08 15:56:55,495 dev_appserver.py] Could not '
            'initialize images API; you are likely missing the Python "PIL" '
            'module. ImportError: No module named _imaging')
    self.assertFalse(tt._IsLaunchCompletedLogLine(line))

  # NOTE: the following pieces of TaskThread are explicitly tested in
  # deploy_controller_unittest.py's testTaskThreadForProject():
  # - use of stdin to on __init__
  # - _TaskWillStart()
  # - _TaskDidStart()
  # - _TaskDidStop(code)


if __name__ == "__main__":
  unittest.main()
