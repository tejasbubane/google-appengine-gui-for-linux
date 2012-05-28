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

"""Deployment controller for the launcher.

The launcher is a project manager for Google App Engine.  This
includes a UI for "New Project" (to create from the template), Run
(locally), and Deploy (to Google).  It also includes general client
support such as auto-update of the SDK.

The Mac download of Google App Engine is the Mac Launcher with the SDK
embedded inside.  This launcher will be for Windows and Linux.

The DeployController class is used for deploying a Google App Engine
application, or sending it off to be run on Google infrastructure.
"""


import logging
import os
import wx
import dialog_controller_base
from wxgladegen import auth_dialog
import launcher


class DeployController(dialog_controller_base.DialogControllerBase):
  """Controller for deployment of a Google App Engine application."""

  def __init__(self, runtime, preferences, project_list, dialog=None):
    """Initialize a DeployController.

    Args:
      runtime: a launcher.Runtime object.
      project_list: A list of projects to deploy.
      dialog: The auth (name/passwd) dialog to use.
        If None, a default is chosen.
    """
    super(DeployController, self).__init__()
    self._runtime = runtime
    self._preferences = preferences
    self._project_list = project_list
    self._authname = None
    self._password = None
    # Dictionaries of frames and threads indexed by project.  A "text
    # frame" is the textual output window (wx.Frame) for the
    # deployment, like a Console window for a running project.
    self._text_frames = {}
    self._task_threads = {}
    # TODO(jrg): if deployment server ever becomes a property of the
    # project, we may need more than one auth dialog.
    self.dialog = dialog or auth_dialog.AuthDialog(None)
    self.MakeBindingsOKCancel()

  def InitiateDeployment(self):
    """Initiate deployment.

    First we ask for a name and password.  Using this data, we run
    appcfg.py (from the Google App Engine SDK) for each selected
    project to deploy it to Google.  The deployment itself is async.

    For now, we always deploy to the default server.  In the future we
    should make the deployment server a preference, or (better yet)
    property of the Project itself.
    TODO(jrg): do it!

    Returns:
      wx.ID_OK or wx.ID_CANCEL (depending on what was clicked in the
        name/password dialog).
    """
    name_pass_return = self._GetNameAndPassword()
    if name_pass_return == wx.ID_OK:
      self._DoDeploy()  # async
    return name_pass_return

  def _ConfigureDialog(self):
    """Configure our dialog in ways we can't do in wxGlade."""
    self.dialog.Centre()  # Not a typo; wx uses UK spelling
    self.dialog.ok_button.SetDefault()
    self._AddDeployServerToTextField(self.dialog.deploy_description)

  def _AddDeployServerToTextField(self, text_field):
    """Add deploy server information to a UI element.

    If the PREF_DEPLOY_SERVER is set in our preferences, set the label
    of a text field to a descriptive string.

    Args:
      text_field: a wx.TextField to display the information
    """
    deploy_server_pref = launcher.Preferences.PREF_DEPLOY_SERVER
    deploy_server = self._preferences.Get(deploy_server_pref)
    if deploy_server:
      text_field.SetLabel('Deploy server: ' + deploy_server)

  def _GetNameAndPassword(self):
    """Display a modal dialog asking for a name and password.

    This info is used for login when deploying the applications; it is
    never saved anywhere.

    Returns:
      wx.ID_OK or wx.ID_CANCEL
    """
    self._ConfigureDialog()
    rtn = self.dialog.ShowModal()
    if rtn == wx.ID_OK:
      self._authname = self.dialog.name_text_ctrl.GetValue()
      self._password = self.dialog.password_text_ctrl.GetValue()
    return rtn

  def _TextFrameForProject(self, project):
    """Return a Frame suitable for display of deploy output.

    Args:
      project: the Project being deployed.
    Returns:
      A wx.Frame for display of task output.
    """
    title = 'Deployment To Google (%s)' % project.name
    text_frame = launcher.TextFrame(title)
    text_frame.DisplayAndBringToFront()
    return text_frame

  def _TaskThreadForProject(self, project, cmd=None):
    """Return a TaskThread suitable for execution of deployment.

    The TaskThread calls back to us with status (e.g. textual output
    of the task).

    Args:
      project: the Project being deployed.
      cmd: The deployment command to use (tuple).  If None, a default
        is chosen.  Probably only non-None in a unit test.
    Returns:
      A TaskThread to run the deployment.
    """
    deploy_server_pref = launcher.Preferences.PREF_DEPLOY_SERVER
    deploy_server = self._preferences.Get(deploy_server_pref)
    realcmd = cmd or self._runtime.DeployCommand(project, self._authname,
                                                 server=deploy_server)
    # For deployment, the password comes in on stdin.
    # subprocess asks for stdin.fileno() which isn't provided by StringIO.
    (read_end, write_end) = os.pipe()
    os.write(write_end, self._password + '\n')
    os.close(write_end) # so we EOF if reading more instead of blocking
    task_thread = launcher.TaskThread(self, project, realcmd,
                                      stdin=os.fdopen(read_end))
    return task_thread

  def _DoDeploy(self):
    """Deploy the project(s) asynchronously.

    Returns:
      False if there is a problem (e.g. no name or password); else True."""
    if not self._authname or not self._password:
      logging.warning('Name or password unset; cannot deploy.')
      return False
    for project in self._project_list:
      # A new DeployController is created for each deploy request so
      # there is no need to worry about a deploy already running for a
      # given project (at least in the context of our _task_frames
      # dictionaries).
      self._text_frames[project] = self._TextFrameForProject(project)
      self._task_threads[project] = self._TaskThreadForProject(project)
      self._task_threads[project].start()
    return True

  def _TaskDidStop(self, project):
    """Called on the main thread when a deploy task has stopped.

    Args:
      project: the project whose deploy task has completed.
    """
    self.DisplayProjectOutput(project, 'You can close this window now.')
    del(self._text_frames[project])
    del(self._task_threads[project])

  def DisplayProjectOutput(self, project, line):
    """Called on the main thread when output from a deploy task is available.

    Args:
      project: the project being deployed.
      line: a line of textual output from deployment.
    """
    self._text_frames[project].AppendText(line)
