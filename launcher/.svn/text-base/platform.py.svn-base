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

"""Platform specific Python for the launcher.

The launcher is a project manager for Google App Engine.  This
includes a UI for "New Project" (to create from the template), Run
(locally), and Deploy (to Google).  It also includes general client
support such as auto-update of the SDK.

The Mac download of Google App Engine is the Mac Launcher with the SDK
embedded inside.  This launcher will be for Windows and Linux.

The Platform class and it's derivatives provides a platform abstraction.
"""


import os
import subprocess
if os.name == 'posix':
  import signal
elif os.name == 'nt':
  import win32api
  import _winreg


class Error(Exception):
  """Error is a base exception class for this module."""


class PlatformException(Error):
  """Exceptional platform condition, such as 'unsupported platform'."""


class PlatformUnimplemented(Error):
  """An override of a platform method is not implemented."""


class Platform(object):
  """Pure virtual base class for platform-specific methods."""

  def __init__(self, briefname, exists=os.path.exists):
    self._briefname = briefname  # short platform name
    self.__exists = exists

  def __call__(self):
    """We are callable and return self.

    This is an implementation detail of how we create a platform singleton.
    See the end of this file for the singleton creator.

    Returns:
      self
    """
    return self

  @staticmethod
  def _PlatformSpecificObject():
    """Create and return a platform-specific object.

    A platform-specific object is a class derived from Platform that
    overrides a few methods.

    Returns:
      A platform-specific subclass of class Platform.

    Raises:
      PlatformException: An unsupported platform.
    """
    if os.name == 'posix':
      if os.uname()[0] == 'Darwin':
        return PlatformMac()
      elif os.uname()[0] == 'Linux':
        return PlatformLinux()
    elif os.name == 'nt':
      return PlatformWin()
    raise PlatformException('unsupported platform')

  def _FindInPath(self, filename, extra_dirs=None):
    """Find the file in the path, or None.

    Args:
      filename: A file basename (e.g. "echo", "ls") we wish to find in our PATH.
      extra_dirs: If given, a list of additional directories to search.

    Returns:
      A fully qualified pathname for the input filename, or None if
      the file cannot be found in the PATH.
    """
    paths = []
    if 'PATH' in os.environ:
      paths += os.environ['PATH'].split(os.pathsep)
    if extra_dirs:
      paths += extra_dirs
    for path in paths:
      fullpath = os.path.join(path, filename)
      if self.__exists(fullpath):
        return fullpath
    return None

  def KillProcess(self, process):
    """Kill the specified process.

    Args:
      process: The subprocess.Popen process to be killed.

    Raises:
      PlatformUnimplemented: Always; should be overridden in subclass.
    """
    raise PlatformUnimplemented()

  def PythonCommand(self):
    """Return a default path to the Python we want to use.

    Return None if we can't find one.
    This method does not look at preference settings.

    Raises:
      PlatformUnimplemented: Always; should be overridden in subclass.
    """
    raise PlatformUnimplemented()

  def AppEngineBaseDirectory(self):
    """Return a path to the base dir of the App Engine SDK, or None.

    Raises:
      PlatformUnimplemented: Always; should be overridden in subclass.
    """
    raise PlatformUnimplemented()

  def PreferencesFile(self, make_parent_directory=True):
    """Filename of our preferences file.

    Args:
      make_parent_directory: If True, mkdir the parent directory if needed.
        Currently only relevant on Windows.

    Raises:
      PlatformUnimplemented: Always; should be overridden in subclass.
    """
    raise PlatformUnimplemented()

  def ProjectsFile(self, make_parent_directory=True):
    """Filename of our projects file.

    Args:
      make_parent_directory: If True, mkdir the parent directory if needed.
        Currently only relevant on Windows.

    Raises:
      PlatformUnimplemented: Always; should be overridden in subclass.
    """
    raise PlatformUnimplemented()

  def OpenCommand(self, path):
    """Command for opening a file or folder on disk.

    Args:
      path: An absolute path to the file or folder.
    Returns:
      A tuple suitable for subprocess.Popen(), or None.

    Raises:
      PlatformUnimplemented: Always; should be overridden in subclass.
    """
    raise PlatformUnimplemented()

  def DefaultEditor(self):
    """Default executable for editing a file.

    Raises:
      PlatformUnimplemented: Always; should be overridden in subclass.
    """
    raise PlatformUnimplemented()

  def EditCommand(self, editor, application):
    """Command for editing an application.

    Args:
      editor: the editor to use
      application: a full path to an application to edit
    Returns:
      A tuple suitable for subprocess.Popen(), or None.

    Raises:
      PlatformUnimplemented: Always; should be overridden in subclass.
    """
    raise PlatformUnimplemented()

  def BriefPlatformName(self):
    """Return a brief platform name.

    Returns:
      A brief string representing our platform.
    """
    return self._briefname

  def IsSuccessfulCommandResultCode(self, code):
    """Whether the result code from a command actually a success.

    Args:
      code: The numerical result code from the subprocess wait() function.
    Returns:
      True iff the result code is considered a success, especially the
      result code returned when the subprocess is intentionally killed.

    Raises:
      PlatformUnimplemented: Always; should be overridden in subclass.
      """
    raise PlatformUnimplemented()


class PlatformPosix(Platform):
  """Common Platform base class for Linux and Mac."""

  def KillProcess(self, process):
    """Kill the specified process, a subprocess.Popen object."""
    os.kill(process.pid, signal.SIGTERM)

  def PythonCommand(self):
    """Return a default path to the Python we want to use.

    Returns:
      A default path to the Python we want to use.
    """
    extra = ('/usr/bin', '/usr/local/bin')
    return self._FindInPath('python', extra)

  def AppEngineBaseDirectory(self):
    """Return a path to the base dir of the App Engine SDK, or None.

    Returns:
      A path to the base dir of the App Engine SDK, or None if not found.
    """
    for dirname in ('/usr/local/google_appengine',):
      if os.path.isdir(dirname):
        return dirname
      return None

  def PreferencesFile(self, make_parent_directory=True):
    """Filename of our preferences file.

    Arg make_parent_directory is ignored (unnecessary), but we retain
    it to keep the signature in sync with the Windows version.

    Returns:
      The filename of our preference file.
    """
    # No need to make the parent directory when it is ~
    return os.path.expanduser('~/.google_appengine_launcher.ini')

  def ProjectsFile(self, make_parent_directory=True):
    """Filename of our projects file.

    Arg make_parent_directory is ignored (unnecessary), but we retain
    it to keep the signature in sync with the Windows version.

    Returns:
      The filename of our projects file.
    """
    # No need to make the parent directory when it is ~
    return os.path.expanduser('~/.google_appengine_projects.ini')

  def IsSuccessfulCommandResultCode(self, code):
    """Is the result code from a command actually a success?

    Args:
      code: The numerical result code from the subprocess wait() function.
    Returns:
      True if the result code is considered a success, especially the
      result code returned when the subprocess is intentionally killed.
      False otherwise
    """
    # zero is the traditional "successful exit code".  Python's subprocess
    # module returns a code of "negative the signal number" when a process
    # is killed by a signal.  The launcher uses signal 15 (SIGTERM) to
    # kill the subprocess on the user's behalf, so it's considered to
    # be successful.
    if code in (0, -15):
      return True
    return False


class PlatformMac(PlatformPosix):
  """Mac-specific platform object."""

  def __init__(self):
    super(PlatformMac, self).__init__('mac')

  def OpenCommand(self, path):
    """Command for opening a file or folder on disk.

    Args:
      path: An absolute path to the file or folder.
    Returns:
      A tuple suitable for subprocess.Popen(), or None.
    """
    return ('/usr/bin/open', path)

  def DefaultEditor(self):
    """Default executable for editing a file.

    Returns: the default editor
    """
    return '/Applications/TextEdit.app'

  def EditCommand(self, editor, application):
    """Edit an application.

    Args:
      editor: the editor to use (ignored on OSX for now)
      application: a full path to an application to edit
    Returns:
      A tuple suitable for subprocess.Popen(), or None.
    """
    # TODO(jrg): implement properly for OSX
    return self.OpenCommand(os.path.join(application, 'app.yaml'))

class PlatformLinux(PlatformPosix):
  """Linux-specific platform object."""

  def __init__(self, exists=os.path.exists):
    super(PlatformLinux, self).__init__('linux', exists=exists)

  def OpenCommand(self, path):
    """Command for opening a file or folder on disk.

    First choice for open command is based on the users DESKTOP_SESSION
    environment variable.  If this environment variable is absent, or either
    of the relevant executables are absent it will default to either one,
    with the gnome browser as the preferred default.

    TODO(rafek): Make the browser user selectable if user wishes.

    Args:
      path: An absolute path to the file or folder.
    Returns:
      A tuple suitable for subprocess.Popen(), or None.
    """
    desktop_session = os.environ.get('DESKTOP_SESSION', 'gnome')
    gnome_opener = self._FindInPath('gnome-open')
    kde_opener = self._FindInPath('konqueror')

    if not(gnome_opener or kde_opener):
      return None
    elif desktop_session == 'kde' and kde_opener:
      executable = kde_opener
    else:
      # Just try to use the first available.
      executable = gnome_opener or kde_opener

    return (executable, path)

  def DefaultEditor(self):
    """Default executable for editing a file.

    Returns: the default editor
    """
    return self._FindInPath('emacs')

  def EditCommand(self, editor, application):
    """Command for editing an application.

    Args:
      editor: the editor to use (ignored on OSX for now)
      application: a full path to an application to edit
    Returns:
      A tuple suitable for subprocess.Popen(), or None.
    """
    return (editor, os.path.join(application, 'app.yaml'))


class PlatformWin(Platform):
  """Win-specific platform object."""

  def __init__(self):
    super(PlatformWin, self).__init__('win')

  def KillProcess(self, process):
    """Kill the specified process, a subprocess.Popen object."""
    PROCESS_TERMINATE = 1   # same name as win32 constant
    handle = win32api.OpenProcess(PROCESS_TERMINATE, False, process.pid)
    win32api.TerminateProcess(handle, -1)
    win32api.CloseHandle(handle)

  def PythonCommand(self):
    """Return a default path to the Python we want to use.

    Note a preference for pythonw.exe instead of python.exe to avoid
    bringing up a console window when the dev_appserver is run.
    pythonw.exe and python.exe are equivalent but pythonw.exe is less
    likely to have a mapping.

    Returns:
      A default path to the Python we want to use or None.
    """
    # Look for a Python set in the registry.  Try and use the highest
    # version available.
    #
    # TODO(jrg):
    # This does NOT find cygwin Python.  Is that OK?  The wxPython
    # packages on the net use the Windows Python (not the cygwin one),
    # so finding the cygwin Python is probably not helpful.  However,
    # we're currently only using the return value to run the
    # dev_appserver, which doesn't care about wx.  Perhaps use of 2
    # different Pythons (one for the launcher, one for the
    # dev_appserver) is not as confusing as it sounds?
    pythonpath = ''
    try:
      basepath = r'SOFTWARE\Python\PythonCore'
      reg = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, basepath)
      (subkeys_count, unused_values, unused_lastmod) = _winreg.QueryInfoKey(reg)

      names = []
      for i in range(subkeys_count):
        names.append(_winreg.EnumKey(reg, i))
      names.sort(reverse=True)  # so the latest version is first
      _winreg.CloseKey(reg)

      reg = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                            basepath + ('\\%s\\' % names[0]))
      install_path = _winreg.QueryValue(reg, 'InstallPath')
      # Try pythonw.exe first.
      pythonpath = os.path.join(install_path, 'pythonw.exe')
      if not os.path.exists(pythonpath):
        pythonpath = os.path.join(install_path, 'python.exe')
      _winreg.CloseKey(reg)
    except WindowsError:
      # It's fine if the registry key doesn't exist -- we'll fall through
      # to _FindInPath().
      pass

    if os.path.exists(pythonpath):
      return pythonpath
    # Try pythonw.exe first.
    for exe in ('pythonw.exe', 'python.exe'):
      pythonpath = self._FindInPath(exe)
      if pythonpath and os.path.exists(pythonpath):
        return pythonpath
    return None

  def AppEngineBaseDirectory(self):
    """Return a path to the base dir of the App Engine SDK, or None.

    Returns:
      A path to the base dir of the App Engine SDK, or None if not found.
    """
    candidate = os.path.dirname(os.getcwd())
    for dirname in (candidate,):
      if (os.path.isdir(dirname) and
          os.path.exists(os.path.join(dirname, 'dev_appserver.py'))):
        return dirname
    return None

  def PreferencesFile(self, make_parent_directory=True):
    """Filename of our preferences file.

    Returns:
      The filename of our preference file.
    """
    # On Windows, expanduser('~') is
    # C:\Documents and Settings\$USER\Application Data\.
    # (Question: should I use os.environ['APPDATA'] instead?
    #  It's the same value but may be "more correct".)
    basedir = os.path.expanduser('~/Google')
    if not os.path.exists(basedir) and make_parent_directory:
      os.mkdir(basedir)
    return os.path.join(basedir, 'google_appengine_launcher.ini')

  def ProjectsFile(self, make_parent_directory=True):
    """Filename of our projects file.

    Returns:
      The filename of our projects file.
    """
    basedir = os.path.expanduser('~/Google')
    if not os.path.exists(basedir) and make_parent_directory:
      os.mkdir(basedir)
    return os.path.join(basedir, 'google_appengine_projects.ini')

  def OpenCommand(self, path):
    """Command for opening a file or folder on disk.

    Args:
      path: An absolute path to the file or folder.
    Returns:
      A tuple suitable for subprocess.Popen(), or None.
    """
    cmd_exe = self._FindInPath('cmd.exe')
    # The empty argument allows cmd.exe to open paths with spaces in them
    # without incident.
    return (cmd_exe, '/c', 'start', '', path)

  def DefaultEditor(self):
    """Default executable for editing a file.

    Returns: the default editor
    """
    # notepad doesn't understand Unix line endings, so try hard to
    # find wordpad (even if not in the path).
    wp = (self._FindInPath('wordpad.exe') or
          'c:/Program Files/Windows NT/Accessories/wordpad.exe')
    if wp:
      return wp
    return self._FindInPath('notepad.exe')

  def EditCommand(self, editor, application):
    """Command for editing an application.

    Args:
      editor: the editor to use (ignored on OSX for now)
      application: a full path to an application to edit
    Returns:
      A tuple suitable for subprocess.Popen(), or None.
    """
    return (editor, os.path.join(application, 'app.yaml'))

  def IsSuccessfulCommandResultCode(self, code):
    """Is the result code from a command actually a success?

    Args:
      code: The numerical result code from the subprocess wait() function.
    Returns:
      True if the result code is considered a success, especially the
      result code returned when the subprocess is intentionally killed.
      False otherwise
    """
    # By observation, the launcher intentionally killing a process on windows
    # results in a return code of -1, so that is one of our success values.
    if code in (0, -1):
      return True
    return False


# Make a singleton.  Note it is callable and returns self.
Platform = Platform._PlatformSpecificObject()
