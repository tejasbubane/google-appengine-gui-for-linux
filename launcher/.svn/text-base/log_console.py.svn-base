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

"""Console window (text output) for the log of a locally running Project.

The launcher is a project manager for Google App Engine.  This
includes a UI for "New Project" (to create from the template), Run
(locally), and Deploy (to Google).  It also includes general client
support such as auto-update of the SDK.

A Project is a Google App Engine Application.
"""


import wx
import text_frame


class LogConsole(text_frame.TextFrame):
  """LogConsole is the output window (view in MVC) for a running project.

  Every LogConsole has exactly one Project associated with
  it.  Projects which nave never launched may not yet have a
  LogConsole associated with them.  (The project does not have to be
  running.)  Closing the project window does not destroy it; is simply
  hidden.  The LogConsole is the only store for project output.
  """

  def __init__(self, project):
    """Create a new LogConsole.

    Args:
      project: the Project associated with this LogConsole.
    """
    title = 'Log Console (%s)' % project.name
    super(LogConsole, self).__init__(title)
    self._project = project
    self.Bind(wx.EVT_CLOSE, self.CloseHandler)

  def CloseHandler(self, event):
    """Called when the user closes this window (frame).

    Log Console windows are the only repository of process output.  If we
    destroy them, the output is lost.  We override the close handler to
    interpret a native "window close" as a "go away"; under the covers
    we really just hide it (and save it for later).

    Called directly from UI so the arg list matches wxPython handler convention.
    """
    if not event.CanVeto():
      self.Destroy()
      # TODO(jrg): tell controller to remove me from its list
    else:
      self.Show(False)
      event.Veto()

  @property
  def project(self):
    """We don't want this property to be reset after init."""
    return self._project
