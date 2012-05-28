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

"""Controller (MVC) for the add new (project) dialog.

A Google App Engine Application is called a 'project' internally to
the launcher to prevent confusion.  Class App is for the launcher
application itself, and class Project is for an App Engine
Application (a 'project')."""


import fileinput
import os
import shutil
import wx
import addexisting_controller
import launcher
from wxgladegen import project_dialogs


class AddNewController(addexisting_controller.AddExistingController):
  """Controller for an Add New Project dialog.

  The controller is responsible for displaying the dialog, filling it
  in, and (if not cancelled) reading data back.  It will then create a
  new project (on disk), and can return a new launcher.Project for it.

  This is much like AddExisting, except:
   - we can specify the name explicitly
   - we actually create the project on disk
  """

  # Error string if runtime not happy
  _NO_SDK_STRING = """
  Cannot create a new project.  App Engine SDK not found.
  Please install the App Engine SDK, or set its location in the Preferences.
  Preferences can be edited from the Edit -> Preferences menu.
  """

  def __init__(self):
    """Init the base class, but specify our extended dialog."""
    add_new_project_dialog = project_dialogs.AddNewProjectDialog
    super(AddNewController, self).__init__(add_new_project_dialog(None))
    self._SetDefaults()

  def _SetDefaults(self):
    """Set some default values for a new project.

    The idea is that a simple YES will work for these default values.
    """
    wxsp = wx.StandardPaths.Get()
    docdir = wxsp.GetDocumentsDir()
    self.SetPath(docdir)
    newname = self._NewProjectNameInDirectory(docdir)
    self.SetName(newname)

  def _NewProjectNameInDirectory(self, dirname):
    """Return a unique name for a project in the directory.

    Args:
      dirname: parent directory to inspect
    Returns:
      A unique name for a project (App) in the directory.
      The name is NOT fully-qualified!
    """
    existing_files = os.listdir(dirname)
    newname = 'engineapp'  # what's a good default name?
    x = 1
    while newname in existing_files:
      newname = 'engineapp-%d' % x
      x += 1
    return newname

  def _BrowseForDirectory(self, evt):
    """Browse for a parent directory for the app, then set this in the dialog.

    Called directly from UI.  Override of AddExisting behavior (new message,
    don't require it to already exist).
    """
    message = 'Pick a parent directory for the new App Engine App'
    path = self.GetPath()  # parent directory of project
    if not os.path.exists(path):
      path = ''
    dirname = wx.DirSelector(message=message,
                             defaultPath=path)
    if dirname:
      self.SetPath(dirname)

  def SetName(self, name):
    """Set the project name in the dialog."""
    self.dialog.app_name_text_ctrl.SetValue(name)

  def GetName(self):
    """Get the project name from the dialog."""
    return self.dialog.app_name_text_ctrl.GetValue()

  def _SanityCheckName(self, name):
    """Sanity check the name (presumably taken from the dialog).

    Args:
      name: a project name to check.
    Returns:
      True if we should make a project from these values.
    """
    if not name:
      self.FailureMessage('Name missing or empty; cannot make project.',
                          'Add New Application')
      return False
    return True

  def _SanityCheckPathDoesNotExist(self, path):
    """Make sure path does not exist.

    Args:
      path: path to check
    Returns:
      True if path does NOT exist.
    """
    if os.path.exists(path):
      self.FailureMessage('Name invalid (already exists)',
                          'Add New Application')
      return False
    return True

  def _NewProjectTemplate(self, preferences=None):
    """Return the new project template directory.

    Args:
      preferences: the preference object to use to find our App Engine SDK.
        If None, a default is chosen.
    Returns:
      A directory name the new project template.
      (Its correctness isn't verified.)
    """
    preferences = preferences or launcher.Preferences()
    basedir = preferences[launcher.Preferences.PREF_APPENGINE]
    if not basedir:
      self.FailureMessage(self._NO_SDK_STRING,
                          'Create new Project');
      return
    templatedir = os.path.join(basedir, 'new_project_template')
    return templatedir

  def _CreateProjectOnDisk(self, newpath, name):
    """Using template files, actually create a project on disk.

    Assumes the path (a directory) already exists.
    Args:
      newpath: directory for the project (to be created)
      name: name to put in the project's app.yaml
    Returns:
      True if successful.
    """
    new_project_template = self._NewProjectTemplate()
    try:
      shutil.copytree(new_project_template, newpath)
    except OSError:
      self.FailureMessage(('Cannot copy template files from %s to %s' %
                           (new_project_template, newpath)),
                          'Create New Project')
      return False
    # Set the project name in the app.yaml.
    # module fileinput magically sets stdout when inplace=1 (see the
    # docs), which makes the logic of these two statements hard to
    # figure out just by looking.  Also note trailing comma in print
    # command so we don't add a 2nd newline.  Quite perlrific!
    for line in fileinput.input(os.path.join(newpath, 'app.yaml'), inplace=1):
      print line.replace('new-project-template', name),
    return True

  def Project(self):
    """Return a project created from interaction with this dialog.

    Returns:
      a launcher.Project, or None.
    Side effect:
      Actually creates the project on disk from the template files.
    """
    if self._dialog_return_value != wx.ID_OK:
      return None
    path = self.GetPath()  # parent directory of project
    port = self.GetPort()
    name = self.GetName()
    if not (self._SanityCheckPort(port) and
            self._SanityCheckPath(path, check_contents=False)):
      return None
    newpath = os.path.join(path, name)
    if not self._SanityCheckPathDoesNotExist(newpath):
      return None
    if not self._CreateProjectOnDisk(newpath, name):
      return None
    return launcher.Project(newpath, port)
