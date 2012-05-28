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

"""Controller (MVC) for the add existing (project) dialog.

A Google App Engine Application is called a 'project' internally to
the launcher to prevent confusion.  Class App is for the launcher
application itself, and class Project is for an App Engine
Application (a 'project').
"""


import os
import wx
import dialog_controller_base
import launcher
from wxgladegen import project_dialogs


class AddExistingController(dialog_controller_base.DialogControllerBase):
  """Controller for an Add Existing Project dialog.

  The controller is responsible for displaying the dialog, filling it
  in, and (if not cancelled) reading data back and creating a new
  launcher.Project.
  """

  def __init__(self, dialog=None):
    """Initialize a new controller.

    Args:
      dialog: the dialog to use.  If None, a default is chosen.
    """
    super(AddExistingController, self).__init__()
    self.dialog = (dialog or project_dialogs.AddExistingProjectDialog(None))
    self.MakeBindings()
    # Make sure we don't create a Project until we've actually OK'd the dialog.
    self._dialog_return_value = None

  def _BrowseForDirectory(self, evt):
    """Browse for a directory, then set its path in the dialog.

    Called directly from UI.
    """
    # Default path is the parent directory
    default_path = self.GetPath()
    if os.path.exists(default_path):
      default_path = os.path.join(default_path, '..')
    else:
      default_path = ''
    # On MacOSX, wx.DD_DIR_MUST_EXIST doesn't appear to be honored.  :-(
    dirname = wx.DirSelector(message='Pick an existing App Engine App',
                             defaultPath=default_path,
                             style=wx.DD_DIR_MUST_EXIST)
    if dirname:
      self.SetPath(dirname)

  def MakeBindings(self):
    """Bind events on our dialog."""
    self.MakeBindingsOKCancel()
    self.dialog.Bind(wx.EVT_BUTTON, self._BrowseForDirectory,
                     self.dialog.app_browse_button)

  def SetPort(self, port):
    """Set the port in the dialog.

    Args:
      port: the port number to use.
    """
    self.dialog.app_port_text_ctrl.SetValue(str(port))

  def SetPath(self, path):
    """Set the path in the dialog.

    Args:
      path: the path to use.
    """
    if not path:
      path = ''
    self.dialog.app_path_text_ctrl.SetValue(path)

  def GetPort(self):
    """Return the port in the dialog."""
    return self.dialog.app_port_text_ctrl.GetValue()

  def GetPath(self):
    """Return the path in the dialog."""
    return self.dialog.app_path_text_ctrl.GetValue()

  def ShowModal(self):
    """Show our dialog modally.

    Returns:
      wx.ID_OK if Update was clicked; wx.ID_CANCEL if Cancel was clicked.
    """
    self._dialog_return_value = self.dialog.ShowModal()
    return self._dialog_return_value

  def _SanityCheckPath(self, path, check_contents=True):
    """Sanity check new values before making a Project.

    Args:
      path: a filesystem path (from the dialog)
      check_contents: if True, check if the contents look valid.
        If invalid, warn, but allow things to continue.
    Returns:
      True if we should make a project from this value.
    """
    if not (path and os.path.isdir(path)):
      self.FailureMessage('Path invalid; cannot make project.',
                          'Add Application')
      return False
    if check_contents and not os.path.exists(os.path.join(path, 'app.yaml')):
      self.FailureMessage('Specified path doesn\'t look like an application; ' +
                          '%s/app.yaml not present.  (Allowing anyway.)' % path,
                          'Add Application')
      # fall through; looks bad but don't deny just in case.
    # We made it!
    return True

  def _SanityCheckPort(self, port):
    """Sanity check new values before making a Project.

    Args:
      port: the port for the project (also from the dialog)
    Returns:
      True if we should make a project from this value.
    """
    try:
      port = int(port)
    except ValueError:
      port = None
    if not port or port < 1024:
      self.FailureMessage('Port invalid (not a number or less than 1024); ' +
                          'cannot make project.',
                          'Add Application')
      return False
    return True

  def Project(self):
    """Return a project created from interaction with this dialog.

    Returns:
      A launcher.Project, or None.
    """
    if self._dialog_return_value != wx.ID_OK:
      return None
    path = self.GetPath()
    port = self.GetPort()
    if not (self._SanityCheckPath(path) and self._SanityCheckPort(port)):
      return None
    return launcher.Project(path, port)
