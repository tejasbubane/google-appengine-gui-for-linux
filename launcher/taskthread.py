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

import os
import re
import subprocess
import time
import threading
import wx
import launcher


# TODO(jrg): rename this file task_thread.py
class TaskThread(threading.Thread):
  """A TaskThread is a thread for managing a task (subprocess).

  This thread creates a subprocess and directs the subprocess output
  to the task controller for display.  All tasks have an associated
  project.

  All callbacks initiated from this class (e.g. DisplayProjectOutput,
  _TaskWillStart) are called on the main thread with wx.CallAfter().
  """

  def __init__(self, controller, project, cmd, stdin=None):
    """Initialize a new TaskThread.

    Args:
      controller: A TaskController (or any controller that responds
        that has a callable AppendText attribute) which
        accepts stdout.
      project: The App Engine project (application) related to this task.
      cmd: A list of executable and args; the command to run in a
        subprocess which starts the app.
      stdin: The file used for stdin of our subprocess.
    """
    super(TaskThread, self).__init__()
    self._controller = controller
    self._project = project
    self._cmd = cmd
    self._stdin = stdin
    self.process = None

  # Override of threading.Thread method so NotToBeCamelCased
  def run(self):
    self._TaskWillStart()
    self.LogOutput('Running command: \"%s\"\n' % str(self._cmd), date=True)
    self.process = subprocess.Popen(self._cmd,
                                    stdin=self._stdin,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
    try:
      started = False
      while True:
        line = self.process.stdout.readline()
        if not line:
          break
        self.LogOutput(line)
        if not started:
          # Don't declare ourselves as 'started' until we see the subprocess
          # announce that it is ready.
          if self._IsLaunchCompletedLogLine(line):
            self._TaskDidStart()
            started = True

    except IOError:
      pass
    # if we get here: process died (or is about to), so thread can die.
    code = self.process.wait()
    self.LogOutput('(Process exited with code %d)\n\n' % code, date=True)
    self._TaskDidStop(code)
    self.process = None

  def _IsLaunchCompletedLogLine(self, line):
    """Is the line that was logged the "hey, we've started!" value?

    Args:
      line: a string, presumably a log line from the subprocess

    Returns:
      True if the line is a special line that indicates that the subprocess
      as started.  False otherwise.
    """
    if re.match('.*Running application.*http://[^:]+:[0-9]+', line):
      return True
    return False

  # Override of threading.Thread method so NotToBeCamelCased
  def stop(self):
    if not self.process:
      return
    platform = self._PlatformObject()
    platform.KillProcess(self.process)

  def _PlatformObject(self):
    """Return a platform object.

    Split out for easier unit testing
    """
    return launcher.Platform()

  def LogOutput(self, line, date=False):
    """Display a given line (typically process output) in the Logs window.

    Args:
      line: a line of text to display for this subprocess / App Engine app
      date: if True, prefix with date.
    """
    if date:
      line = time.strftime("%Y-%m-%d %X") + ' ' + line
    wx.CallAfter(self._controller.DisplayProjectOutput, self._project, line)

  def _TaskWillStart(self):
    """If our controller has a _TaskWillStart, call it on the main thread.

    The controller's property is called with our project as an arg.
    This method is called right before the task is started."""
    attr = getattr(self._controller, '_TaskWillStart', None)
    if attr and callable(attr):
      wx.CallAfter(attr, self.project)

  def _TaskDidStart(self):
    """If our controller has a _TaskDidStart, call it on the main thread.

    The controller's property is called with our project as an arg.
    This method is called right after the task is started."""
    attr = getattr(self._controller, '_TaskDidStart', None)
    if attr and callable(attr):
      wx.CallAfter(attr, self.project)

  def _TaskDidStop(self, code):
    """If our controller has a _TaskDidStop, call it on the main thread.

    The controller's property is called with our project and the
    task result code as arguments.
    This method is called right after the task has stopped."""
    attr = getattr(self._controller, '_TaskDidStop', None)
    if attr and callable(attr):
      wx.CallAfter(attr, self.project, code)

  @property
  def project(self):
    """A taskthread's project is read-only."""
    return self._project
