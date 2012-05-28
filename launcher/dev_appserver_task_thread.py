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

"""DevAppServerTaskThread is a TaskThread for running
dev_appserver.py, the local development App Engine back-end.  It
overrides a few methods to insure the UI is updated properly to
reflect run state.
"""


import wx
import launcher
import taskthread


class DevAppServerTaskThread(taskthread.TaskThread):
  """A dev_appserver.py task thread for a Project (App Engine App)."""

  def _TaskWillStart(self):
    """Update the UI to reflect that our project is launching."""
    assert(self._project.runstate in
           (launcher.Project.STATE_STOP, launcher.Project.STATE_DIED))
    self._ChangeProcessRunState(launcher.Project.STATE_STARTING)

  def _TaskDidStart(self):
    """Update the UI to reflect that our project has started running."""
    self._ChangeProcessRunState(launcher.Project.STATE_RUN)

  def _TaskDidStop(self, returncode):
    """Update the UI to reflect that our project has stopped.

    Update the UI to reflect that the project has stopped, determining
    how it exited (failure / success) by looking at the return code.

    Args:
      returncode: The proces return (exit) code of the process this thread
                  is monitoring.
    """
    if launcher.Platform().IsSuccessfulCommandResultCode(returncode):
      self._ChangeProcessRunState(launcher.Project.STATE_STOP)
    else:
      self._ChangeProcessRunState(launcher.Project.STATE_DIED)

  def _ChangeProcessRunState(self, state):
    """Change the process run state and update the UI.

    We need to only update the UI only in the main thread, so we use
    wx.CallAfter().

    Args:
      state: the new run state (e.g. launcher.STOP, launcher.RUN)
    """
    self.project.runstate = state
    wx.CallAfter(self._controller.RunStateChanged, self.project)
