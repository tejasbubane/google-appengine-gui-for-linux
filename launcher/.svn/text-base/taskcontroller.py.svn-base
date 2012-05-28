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
import subprocess
import webbrowser
import wx
import launcher


# TODO: rename this file task_controller.py in a big renameathon
class TaskController(object):
  """Main conroller (MVC) for running tasks.

  Tasks are running instances of App Engine projects.
  """

  def __init__(self, app_controller):
    """Create a new TaskController.

    Args:
      app_controller: the main application controller.
     """
    self._app_controller = app_controller
    # self._frame: the main frame for project display
    # self._threads: an array of threads for running App Engine applicatons
    # self._consoles: an array of LogConsoles for App Engine applications
    self._frame = None
    self._threads = []
    self._consoles = []
    self._runtime = None
    self._platform = launcher.Platform()
    self._preferences = None

  def SetModelsViews(self, frame=None, runtime=None, platform=None,
                     preferences=None):
    """Set models and views (MVC) for this controller.

    We need a pointer to the main frame.  We can't do in __init__
    since those objects wants a pointer to me as well, and one must
    come first.  Convention for launcher is for model/view to take
    controllers in their __init__, and have the controller accept it
    later with a call to SetModelsViews().

    Args:
     frame: the main frame (MainFrame) for the app
     runtime: a launcher.Runtime
     platform: a launcher.Platform
     preferences: a launcher.Preferences
    """
    if frame:
      self._frame = frame
    if runtime:
      self._runtime = runtime
    if platform:
      self._platform = platform
    if preferences:
      self._preferences = preferences

  def _GenericRun(self, extra_flags=None):
    """Run the project(s) selected in the main frame.

    Args:
      extra_flags: a list of extra command line flags for the run command
    """
    for project in self._frame.SelectedProjects():
      cmd = None
      err = ""
      try:
        if self._FindThreadForProject(project):
          logging.warning('Already running a task for %s!' % project.path)
        else:
          cmd = self._runtime.DevAppServerCommand(project,
                                                  extra_flags=extra_flags)
      except launcher.RuntimeException, r:
        err = r.message
      if not cmd or err:
        logging.error(err + '\n'
                      'Cannot run project %s.  Please confirm '
                      'these values in your Preferences, or take an '
                      'appropriate measure to fix it (e.g. install Python).'
                      % project.path)
      else:
        t = self._CreateTaskThreadForProject(project, cmd)
        t.start()
        self._threads.append(t)

  def _OpenFile(self, path, run_open_cmd):
    """Open file in browser.

    Will launch external browser in platform dependent manner.

    Args:
      path: Absolute path to open.
    """
    opencmd = self._platform.OpenCommand(path)
    if not opencmd:
      logging.warning('Could not form an open command, sorry')
      return
    run_open_cmd(opencmd)

  def OpenSDK(self, event, run_open_cmd=subprocess.Popen):
    """Open SDK in browser.

    Called from UI menu.
    """
    sdk_dir = self._platform.AppEngineBaseDirectory()
    self._OpenFile(sdk_dir, run_open_cmd)

  def Run(self, event):
    """Run the project(s) selected in the main frame.

    Called directly from UI.
    """
    self._GenericRun()

  def RunStrict(self, event):
    """Run the project(s) selected in the main frame, strictly.

    Called directly from UI.
    """
    self._GenericRun(['--require_indexes'])

  def _CreateTaskThreadForProject(self, project, cmd):
    """Create and return a task thread, for executing cmd on project.

    Assumes the task thread is for running dev_appserver.
    Split into a seperate method to make unit testing of self.Run() easier.

    Args:
      project: the Project that needs a thread
      cmd: list of exec and args; the command to execute,
        associated with the project
    """
    return launcher.DevAppServerTaskThread(self, project, cmd)

  def Stop(self, event):
    """Stop the project(s) selected in the main frame.

    Called directly from UI.
    """
    for project in self._frame.SelectedProjects():
      thread = self._FindThreadForProject(project)
      if not thread:
        if project.runstate == launcher.Project.STATE_DIED:
          # Just clearing out a stop.
          project.runstate = launcher.Project.STATE_STOP
          self.RunStateChanged(project)
        else:
          logging.warning('Cannot find a running task for %s!' % project.path)
      else:
        thread.stop() # async
    pass

  def Browse(self, event):
    """Browse the project(s) selected in the main frame if they are running.

    Called directly from UI.
    """
    project_list = [p for p in self._frame.SelectedProjects()
                    if p.runstate == launcher.Project.STATE_RUN]
    if not project_list:
      logging.warning('No selected projects are running ' +
                      'so we have nothing to Browse.')
      return
    for project in project_list:
      self._BrowseProject(project)

  def _FindOrCreateConsole(self, project):
    """Find and return the launcher.LogConsole for project; create if needed.

    Args:
      project: the Project associated (or to be associated with) the LogConsole
    """
    for console in self._consoles:
      if project == console.project:
        return console
    console = launcher.LogConsole(project)
    self._consoles.append(console)
    return console

  def StopAll(self, _=None):
    """Stop all projects.

    Args:
      _: not used (made consistent with Stop/Run for easier testing)
    """
    [t.stop() for t in self._threads]  # t.stop() is async.

  def _FindThreadForProject(self, project):
    """Find and return the launcher.TaskThread for project, or None.

    Args:
      project: the project whose thread we are looking for
    """
    for thread in self._threads:
      if thread.project == project:
        return thread
    return None

  def Logs(self, event):
    """Display the Console window for the project(s) selected in the main frame.

    Called directly from UI.
    """
    for project in self._frame.SelectedProjects():
      console = self._FindOrCreateConsole(project)
      console.DisplayAndBringToFront()

  def SdkConsole(self, event):
    """Opens the local SDK Administration console.

    The Console is opened for the project(s) selected in the main frame.
    The URL looks something like http://localhost:PORT/_ah/admin.
    Called directly from UI.
    """
    project_list = [p for p in self._frame.SelectedProjects()
                    if p.runstate == launcher.Project.STATE_RUN]
    if not project_list:
      logging.warning('No selected projects are running ' +
                      'so we have no Admin Console to go to.')
      return
    for project in project_list:
      self._BrowseAdminConsoleForProject(project)

  def Edit(self, event, run_edit_cmd=subprocess.Popen):
    """Opens, for edit, the project(s) selected in the main frame.

    Called directly from UI.

    Args:
      event: a wxPython event (for all Bind()ings)
      run_edit_cmd: the command used to run the actual tuple edit command.
        Only ever set to the non-default in a unit test.
    """
    for project in self._frame.SelectedProjects():
      editor = self._preferences[launcher.Preferences.PREF_EDITOR]
      editcmd = self._platform.EditCommand(editor, project.path)
      if not editcmd:
        logging.warning('Could not form an edit command, sorry')
        return
      run_edit_cmd(editcmd)

  def Open(self, event, run_open_cmd=subprocess.Popen):
    """Opens (in Explorer) the the project(s) selected in the main frame.

    Called directly from UI.

    Args:
      event: a wxPython event (for all Bind()ings)
      run_open_cmd: the command used to run the actual tuple open command.
        Only ever set to the non-default in a unit test.
    """
    for project in self._frame.SelectedProjects():
      self._OpenFile(project.path, run_open_cmd)

  def Deploy(self, event, deploy_controller=None):
    """Initiates a deploy to Google of the project selected in the main frame.

    Called directly from UI.

    Args:
      event: the wx.Event that initiated the transaction
      deploy_controller: if not None, the controller to be used for
        deployment.  If None, a default is used
        (launcher.DeployController).  Only non-None in a unit test.
    """
    project_list = self._frame.SelectedProjects()
    if not project_list:
      logging.warning('No projects selected for deployment.')
      return
    dc = deploy_controller or launcher.DeployController(self._runtime,
                                                        launcher.Preferences(),
                                                        project_list)
    dc.InitiateDeployment()

  def Dashboard(self, event):
    """Opens the App Engine Dashboard for the currently selected project(s).

    The Dashboard is a System Status page for a deployed application
    that lives on a Google server.  See
    http://code.google.com/appengine/kb/status.html for more info.
    A typical URL is https://appengine.google.com/dashboard?app_id=ID
    Called directly from UI.
    """
    for project in self._frame.SelectedProjects():
      self._BrowseDashboardForProject(project)

  def RunStateChanged(self, project):
    """Called when the runstate of a project was changed and UI update is needed.

    Args:
      project: the project whose run state has changed
    """
    self._app_controller.RefreshMainView()
    self._DeleteThreadIfNeeded(project)

  def _DeleteThreadIfNeeded(self, project):
    """If we have a thread for the project and it isn't running, delete it.

    Args:
      project: the project whose thread is no longer needed
    """
    if project.runstate in (launcher.Project.STATE_STOP,
                            launcher.Project.STATE_DIED):
      thread = self._FindThreadForProject(project)
      if thread:
        self._threads.remove(thread)

  def _PlatformObject(self):
    """Return a platform object.

    Split out for easier unit testing.
    """
    return launcher.Platform()

  def _BrowseProject(self, project, browsefunc=webbrowser.open):
    """Unconditionally browse the specified project.

    Args:
      project: the project we want to browse
      browsefunc: if set, use as a browsing function that takes 1 arg, a URL
    """
    browsefunc('http://localhost:%d' % project.port)

  def _BrowseAdminConsoleForProject(self, project, browsefunc=webbrowser.open):
    """Unconditionally browse the SDK Administration Console for the project.

    Args:
      project: the project whose admin console we want to browse
      browsefunc: if set, use as a browsing function that takes 1 arg, a URL
    """
    browsefunc('http://localhost:%d/_ah/admin' % project.port)

  def _BrowseDashboardForProject(self, project, browsefunc=webbrowser.open):
    """Unconditionally browse the Dashoard for the project.

    The Dashboard is a System Status page for a deployed application
    that lives on a Google server.

    Args:
      project: the project whose Dashboard we want to browse
      browsefunc: if set, use as a browsing function that takes 1 arg, a URL
    """
    server = (self._preferences[launcher.Preferences.PREF_DEPLOY_SERVER] or
              'appengine.google.com')
    # TODO(jrg): make the path configurarable on a per-project basis
    browsefunc('https://%s/dashboard?app_id=%s'
               % (server, str(project.name)))

  def DisplayProjectOutput(self, project, text):
    """For the output from |project|, send to the appropriate UI.

    Args:
      project: the project whose output we now have
      text: the output from the project that needs display
    """
    console = self._FindOrCreateConsole(project)
    console.AppendText(text)
