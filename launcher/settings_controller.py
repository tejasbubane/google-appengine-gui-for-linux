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

"""Controller (MVC) for the project settings dialog.

A Google App Engine Application is called a 'project' internally to
the launcher to prevent confusion.  Class App is for the launcher
application itself, and class Project is for an App Engine
Application (a 'project').
"""


import re
import wx
import dialog_controller_base
import launcher
from wxgladegen import project_dialogs


class SettingsController(dialog_controller_base.DialogControllerBase):
  """Controller for a project settings dialog.

  The controller is responsible for displaying the dialog, filling it
  in, and (if not cancelled) reading data back and filling in a
  project with changes.
  """

  def __init__(self, project):
    """Initialize a settings controller.

    Args:
      project: a launcher.Project to view and edit
    """
    super(SettingsController, self).__init__()
    self._project = project
    self.dialog = project_dialogs.ProjectSettingsDialog(None)
    self.UpdateDialog()
    self.MakeBindingsOKCancel()

  def UpdateDialog(self):
    """Update the dialog with values from our project."""
    self.dialog.app_name_text_ctrl.SetValue(self._project.name)
    self.dialog.app_path_text_ctrl.SetValue(self._project.path)
    self.dialog.app_port_text_ctrl.SetValue(str(self._project.port))
    flagstring = ' '.join(self._project.flags) or ''
    self.dialog.full_flag_list_text_ctrl.SetValue(flagstring)

  def _UpdateProject(self):
    """Update our project with values from the dialog.

    This method is not called if the dialog is cancelled.
    """
    # TODO(jrg): yell about bad looking flags?
    port = int(self.dialog.app_port_text_ctrl.GetValue())
    flags = self._ParseFlags(self.dialog.full_flag_list_text_ctrl.GetValue())
    if port != self._project.port or flags != self._project.flags:
      if self._project.runstate != launcher.Project.STATE_STOP:
        # TODO(jrg): what's the best UE for this?
        # Deny (below), or stop it and continue?
        self.FailureMessage('Cannot change properties while running; '
                            'operation cancelled.',
                            'Application Edit')
        return
      self._project.port = port
      self._project.flags = flags

  def _ParseFlags(self, flagstring):
    """Parse command line flags from a string of flags.

    Simple answers (e.g. flagstring.split(' ')) doesn't handle spaces in paths.

    Args:
      flagstring: a string of command line flags
    Returns:
      A tuple of command line flags
    """
    # TODO(jrg): try and be friendly for windows pathnames that may
    # have spaces.  For now, require all commands to begin with - or
    # --, assume paths with spaces have only one space in a row, and
    # assume no path in a command line has a space followed by a -.
    early_cmds = re.split(r'\s+', flagstring)
    prev = None
    cmds = []
    for cmd in early_cmds:
      if cmd.startswith('-'):
        # Found a new one.  Flush the previous (if any) and save.
        if prev:
          cmds.append(prev)
        prev = cmd
      else:
        # Continuing a command, stick in when an embedded space
        if prev:
          prev = prev + ' ' + cmd
        else:
          # continuing but nothing there yet???
          prev = cmd
    # done; be sure to flush remaining.
    if prev:
      cmds.append(prev)
    return cmds

  def ShowModal(self):
    """Show our dialog modally; if ended with 'Update', update our project.

    Returns:
      wx.ID_OK if Update was clicked; wx.ID_CANCEL if Cancel was clicked.
    """
    rtn = self.dialog.ShowModal()
    if rtn == wx.ID_OK:
      self._UpdateProject()
    return rtn
