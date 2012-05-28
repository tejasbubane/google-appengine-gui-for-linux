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
import re
import sys
import urllib
import wx
import launcher


class App(wx.App):
  """The main wx.App."""

  # Awkwardly, wx.App.__init__ calls OnInit().
  # Keep that in mind if writing an App.__init__.
  # Thus, "basic __init__() stuff" is in here.
  def OnInit(self):
    """Create top-level objects (e.g. main model, view, and controller objects).
    Logically similar to a 'load nib and set IBOutlets'.
    Note that views (MainFrame) have pointers to controllers, and these same
    controllers have pointers to the views.  To break this cycle,
    we have a convention:
       VIEWS take controllers as input args for __init__,
       CONTROLLERS have SetViewName() methods.

    (Why not the other way round?  Because views like to self.Bind()
    to a controller at __init__, whereas controllers generally do
    nothing on __init__.)
    """
    self._table = None           # a MainTable for our data (M)
    self._project_frame = None   # the main view for our projects (V)
    self._task_controller = None # a TaskController (C)
    self._app_controller = None  # AppController, the main app controller (C)

    self._InitializeLogging()
    self._SetCorrectDirectory()
    self._CreateModels()
    self._CreateControllers()
    self._CreateViews()
    self._ConnectControllersToModelsViews()
    self._DisplayMainFrame()
    self._VersionCheck()
    return True

  def Initialized(self):
    """Return whether we have been initialized properly."""
    # TODO(jrg): if we agree on py2.5, use all().  (My current Linux
    # comes with py2.4, and it's a pain to compile wxWidgets from
    # scratch on a 32/64 machine).
    for attr in ('_table', '_project_frame',
                 '_task_controller', '_app_controller'):
      if not getattr(self, attr):
        return False
    return True

  def _InitializeLogging(self):
    """Initialize a GUI-oriented warning mechanism.

    If this method isn't called, the launcher's warning mechanism
    defaults to text output (to be unittest friendly).  This method
    redirects warnings to dialog boxes to notify the user of a
    problem.
    """
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    handler = launcher.DialogHandler(level=logging.WARNING)
    logging.getLogger('').addHandler(handler)

  def _SetCorrectDirectory(self):
    """Set the correct current directory for launcher happiness.

    Some items, like the toolbar, reference icons with a relative
    path.
    Do nothing if this is a unit test run.
    """
    if not sys.argv[0].endswith('_unittest.py'):
      dirname = os.path.abspath(os.path.dirname(sys.argv[0]))
      os.chdir(dirname)

  def _CreateModels(self):
    """Create models (MVC) for this application."""
    self._table = launcher.MainTable()
    self._preferences = launcher.Preferences()
    self._runtime = launcher.Runtime(preferences=self._preferences)

  def _CreateControllers(self):
    """Create controllers (MVC) for this application."""
    self._app_controller = launcher.AppController(self)
    self._task_controller = launcher.TaskController(self._app_controller)

  def _CreateViews(self):
    """Create views (MVC) for this application.

    Assumes M and C have been created.
    """
    self._project_frame = launcher.MainFrame(
        None,
        -1,
        table=self._table,
        preferences=self._preferences,
        app_controller=self._app_controller,
        task_controller=self._task_controller)

  def _ConnectControllersToModelsViews(self):
    """Tell controller about views and data which may have been created later.

    This prevents a cyclic dependency.
    """
    self._task_controller.SetModelsViews(frame=self._project_frame,
                                         runtime=self._runtime,
                                         preferences=self._preferences)
    self._app_controller.SetModelsViews(frame=self._project_frame,
                                        table=self._table,
                                        preferences=self._preferences)

  def _DisplayMainFrame(self):
    # Last chance to get UI up!
    self._app_controller.RefreshMainView()
    self._project_frame.Show()
    self.SetTopWindow(self._project_frame)

  def _VersionCheck(self, url=None, always_dialog=False):
    """Quick check of version; yell if mismatch.

    Example format from the default URL:
      release: "1.2.3"
      timestamp: 1243913623
      api_versions: ['1']

    Args:
      url: URL to find the latest version; if None, use a default.
      always_dialog: If True, always bring up a dialog even if
        versions match.  Else only bring up a dialog on mismatch.
    """
    url = url or 'http://appengine.google.com/api/updatecheck'
    try:
      url_file = urllib.urlopen(url)
    except IOError:
      new_version_data = 'cannot_contact_server'
    else:
      new_version_data = url_file.read()
    current_version_data = self._CurrentVersionData()

    # Watch out for a 404 or undefined SDK
    if ((not 'api_versions' in new_version_data) or
        (not 'api_versions' in current_version_data)):
      if always_dialog:
        logging.warning('Cannot perform proper version check.')
        logging.warning(new_version_data)
        logging.warning(current_version_data)
      return
    my_timestamp = self._TimestampFromVersionData(current_version_data)
    new_timestamp = self._TimestampFromVersionData(new_version_data)
    if my_timestamp < new_timestamp:
      self._NewVersionNeeded(current_version_data,
                             new_version_data,
                             always_dialog)
    else:
      if always_dialog:
        self._NoNewVersionNeeded(current_version_data)

  def _TimestampFromVersionData(self, data):
    """Return an timestamp from the given VERSION data.

    Returns:
      timestamp as an int, or 0 if none found.
    """
    for line in data.split('\n'):
      if 'timestamp' in line:
        try:
          return int(line.split()[1])
        except IndexError:
          pass  # lost part of our VERSION file?
        except ValueError:
          pass  # no longer using an int as a timestamp?
    return 0

  def _CurrentVersionData(self):
    """Read current version data.

    Returns:
      Contents of the SDK's VERSION file, or an "old" version.
    """
    sdk_dir = self._preferences[launcher.Preferences.PREF_APPENGINE]
    if not sdk_dir:
      return 'Cannot find SDK VERSION file.'
    sdk_version_file = os.path.join(sdk_dir, 'VERSION')
    try:
      data = open(sdk_version_file).read()
      return data
    except IOError:
      return 'release: "0"\ntimestamp: 0\napi_versions: [\'1\']'

  def _NewVersionNeeded(self, old_version, new_version, always_dialog):
    """Tell the user a new version of the SDK is needed.

    Args:
      old_version: our version data.
      new_version: the latest version data available.
      always_dialog: If True, always show the dialog even if disabled
        by a preference.
    """
    message = """
A new version of Google App Engine is available.
Please visit http://code.google.com/appengine/downloads.html

Current:
%s

Latest:
%s
"""
    if (self._preferences[launcher.Preferences.PREF_NOVERSIONCHECK] and
        not always_dialog):
      return
    # TODO(jrg): add a checkbox to disable the update check.
    # See preferences.py for info on eding your preference file.
    # Add a "noversioncheck = True" line to disable it.
    logging.warning(message % (old_version, new_version))

  def _NoNewVersionNeeded(self, version_data):
    """Tell the user NO new version of the SDK is needed.

    Args:
      old_version: our version data.
    """
    message = """
Your Google App Engine SDK is up to date.

Version:
%s
"""
    logging.warning(message % (version_data))

  def OnExit(self):
    """Called when the app will exit."""
    self._task_controller.StopAll(None)
    self.ExitMainLoop()
