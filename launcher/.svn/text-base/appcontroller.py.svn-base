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

import logging
import os
import shutil
import sys
import urllib
import webbrowser
import wx
import launcher


class AppController(object):
  """Main application controller (MVC).

  Provides logic for non-task related app action, such as adding a new
  project.
  """

  def __init__(self, app):
    """Create a new AppController.

    Args:
      app: the wx.App object
    """
    self._app = app
    self._frame = None  # main view for our projects
    self._table = None  # main model for our projects
    self._preferences = None  # main prefs object for this app
    app.Bind(wx.EVT_ACTIVATE_APP, self.OnActivateApp)

  def SetModelsViews(self, frame=None, table=None, preferences=None):
    """Set models and views (MVC) for this controller.

    We need a pointer to the main frame and main table.  We can't do
    in __init__ since those objects wants a pointer to me as well, and
    one must come first.  Convention for launcher is for M/V to take
    controllers in their __init__, and have C take it later.

    Args:
     frame: The main frame (MainFrame) for the app
     table: The main table (MainTable) for the app
     preferences: the Preferences object for the app
    """
    if frame:
      self._frame = frame
    if table:
      self._table = table
    if preferences:
      self._preferences = preferences

  def Add(self, event, path=None):
    """Add an existing project.  Called directly from UI."""
    project = self._AskForProject(launcher.AddExistingController(), path)
    if project:
      self._table.AddProject(project)
      self.RefreshMainView()

  def AddNew(self, event):
    """Add a new project.  Called directly from UI."""
    project = self._AskForProject(launcher.AddNewController())
    if project:
      self._table.AddProject(project)
      self.RefreshMainView()

  def _AskForProject(self, add_controller, path=None):
    """Ask the user for a project using the specified controller.

    Args:
      add_controller: A class to use as the Add Project Controller for
        our dialog.
      path: A file sytem path to pre-poplate the controller's path with.
    Returns:
      A launcher.Project, or None.
    """
    add_controller.SetPath(path)
    add_controller.SetPort(self._table.UniquePort())
    if add_controller.ShowModal() == wx.ID_OK:
      return add_controller.Project()
    else:
      return None

  def _ConfirmRemove(self, message, caption):
    """Confirm the deletion of the projects by asking the user.

    Args:
      message: main text for the dialog
      caption: caption for this dialog
    Returns:
      Whether we should delete
    """
    wx_rtn = wx.MessageBox(message, caption, style=wx.YES_NO|wx.ICON_QUESTION)
    if wx_rtn == wx.YES:
      return True
    return False

  def Remove(self, event):
    """Remove the currently selected application from our list.

    Does NOT delete the files from disk.  Called directly from UI.
    """
    projects = self._frame.SelectedProjects()
    if not projects:
      return
    caption = 'Really delete these projects?'
    disk_not_touched = '(Files on disk will not be touched.)'
    project_descriptions = []
    for project in projects:
      project_descriptions.append('  %s\n' % project.name)
    message = '%s\n\n%s' % (' '.join(project_descriptions),
                            disk_not_touched)
    if self._ConfirmRemove(message, caption):
      for project in projects:
        self._table.RemoveProject(project)
      # Selection is out of sync with projects, so clear it out.
      self._frame.UnselectAll()
      self.RefreshMainView()

  def _FailureMessage(self, message, caption):
    """Display a warning to the user about a non-fatal failure.

    Split into a seperate method for easier unit testing.
    """
    wx.MessageBox(message, caption, style=wx.OK|wx.ICON_ERROR)

  def Settings(self, event, settings_controller=None):
    """Show and edit settings for the currently selected application.

    Called directly from UI.
    Args:
      event: the wx.Event that initiated this callback
      settings_controller: a class to use as the Settings Controller
        for our dialog.  Likely only used for unit testing.
    """
    projects = self._frame.SelectedProjects()
    if len(projects) != 1:
      self._FailureMessage('Exactly one application should be selected '
                           'when choosing to view or edit settings.',
                           'Settings Failed')
      return
    project = projects[0]
    sc = settings_controller or launcher.SettingsController(project)
      # If possibly modified (rtn is ID_OK) we need to refresh the UI.
    if sc.ShowModal() == wx.ID_OK:
      # In MVC, we are Controller.  First, update the View.
      # (The Mac launcher has KVO to do this automagically.)
      self.RefreshMainView()
      # Then update the Model.
      self._table.SaveProjects()

  def RefreshMainView(self):
    """Refresh the main view with data from our model."""
    # TODO(jrg): ARGH!  Access of private member
    self._frame.RefreshView(self._table._projects)

  def OnOpenSDK(self, evt):
    """Called (indirectly) from the Open SDK in Explorer menu item."""
    self._app.OnOpenSDK(evt)

  def OnExit(self, evt):
    """Called (indirectly) from the Exit menu item."""
    self._app.OnExit()

  def OnPreferences(self, evt, pref_controller=None):
    """Called from the Preferences menu item.

    Although wx.EVT_* handlers only take 2 args (including self), we add
    an extra arg (with a default value) to allow easier unit testing.
    """
    controller = (pref_controller or
                  launcher.PrefController(self._preferences))
    controller.ShowModal()

  def OnAbout(self, evt, about_controller=None):
    """Called from the About menu item.

    Although wx.EVT_* handlers only take 2 args (including self), we add
    an extra arg (with a default value) to allow easier unit testing.
    """
    controller = (about_controller or launcher.AboutBoxController())
    controller.ShowModal()

  def OnActivateApp(self, evt):
    """Called when the application active state changes.

    Verify all projects on disk (to see if they still exist, or
    have had their names changed).  When done, update the view.
    """
    # Note: this is not called for initial activation (on launch).
    if evt.GetActive():
      self._table.Verify()
      self.RefreshMainView()

  def Help(self, event):
    """Help on the launcher.  Called directly from the UI."""
    helpdir = os.path.join(os.path.dirname(sys.argv[0]), 'help/index.html')
    helpdir = urllib.pathname2url(os.path.realpath(helpdir))
    webbrowser.open('file:' + helpdir)

  def AppEngineHelp(self, event):
    """Help on App Engine.  Called directly from the UI."""
    webbrowser.open('http://code.google.com/appengine/docs/')

  def Demos(self, event):
    """Called by the stub demo menu item.

    If we have any demos, the stub will have been replaced.
    """
    logging.warning('No demos are available.')

  def InstallDemoByName(self, path, dest_dir=None, prompt=True):
    """Called by a demo sub-menu item.

    Copies the specified demo and adds to the current project list.

    Args:
      path: A full path to the demo we want to use.
      dest_dir: The destination directory for the demo to be copied, or
        None to use a default.
      prompt: Solicit the user before copying the demo files.
        Exists for unit tests to avoid a modal dialog.
    """
    # Find a destination path; ensure it is unique.
    dest_dir = dest_dir or wx.StandardPaths.Get().GetDocumentsDir()
    basename = os.path.basename(path)
    existing_files = os.listdir(dest_dir)
    count = 1
    newname = basename
    while newname in existing_files:
      newname = '%s-%d' % (basename, count)
      count += 1
    newpath = os.path.join(dest_dir, newname)

    if prompt:
      # Ask the user before doing anything.
      caption = 'Install Google App Engine demo?'
      message = ('Google App Engine Launcher wishes to copy the demo "%s" '
                 'to %s' % (basename, newpath))
      allow_copy_dialog = wx.MessageDialog(None, message, caption,
                                           wx.OK | wx.CANCEL | wx.ICON_QUESTION)
      if allow_copy_dialog.ShowModal() != wx.ID_OK:
        return

    # Copy over, create a project, and add it to our table.
    shutil.copytree(path, newpath)
    project = launcher.Project(newpath, self._table.UniquePort())
    self._table.AddProject(project)
    self.RefreshMainView()

  def CheckForUpdates(self, event):
    self._app._VersionCheck(always_dialog=True)
