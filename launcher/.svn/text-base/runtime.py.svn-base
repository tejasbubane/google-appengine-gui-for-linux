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
import logging
import wx
import launcher

class RuntimeException(launcher.Error):
  """Exceptional runtime condition."""

class Runtime(object):
  """Google App Engine runtime management.

  Example:
    - return a command to run the dev_appserver.py with a given project
  """

  # error string if runtime not happy
  _REQ_FAIL_STRING = """
  Warning: Prerequisites for App Engine development are missing!

  A valid python binary must be available.  In addition,
  the App Engine SDK must be installed.  Here are the current
  values we found:

    python = %s
    App Engine SDK root = %s

  Please install the missing pieces and restart the launcher.
  If these are installed but the Launcher failed to find them,
  you can configure their location by editing Launcher preferences.

  The Launcher preferences can be modified by selecting Edit > Preferences.
  """

  def __init__(self, preferences=None):
    """Initialize a Runtime object.

    Args:
      preferences: An object with a dictionary 'get' interface
        for preferences (such as launcher.Preferences); created if None.
    """
    self._preferences = preferences or launcher.Preferences()
    # The preferences object will use a default value if not set
    # when accessed with the __getitem__ interface.
    python = self._preferences[launcher.Preferences.PREF_PYTHON]
    appengine = self._preferences[launcher.Preferences.PREF_APPENGINE]
    if not python or not appengine:
      self._RequirementProblem(self._REQ_FAIL_STRING % (python, appengine))
    else:
      self._ConfigureEnvironment()

  def _ConfigureEnvironment(self):
    """Configure the environment for future subprocesses."""
    sdk_env_setting = self._GetSDKEnvironmentSetting()
    # APPCFG_SDK_NAME is read by appcfg.py
    os.putenv('APPCFG_SDK_NAME', sdk_env_setting)

  def _GetSDKEnvironmentSetting(self):
    """Return a brief string describing our SDK environment.

    Returns:
      a string suitable for setting in an environment variable, or '???'.
    """
    sdk_version = '???'
    sdk_dir = self._preferences[launcher.Preferences.PREF_APPENGINE]
    if sdk_dir:
      sdk_version_file = os.path.join(sdk_dir, 'VERSION')
      try:
        words = open(sdk_version_file).readline().split()  # version: "1.1.9"
        if len(words) == 2:
          sdk_version = words[1].replace('"', '')  # 1.1.9
      except IOError:
        pass
    sdk_env_setting = ('%s-launcher-%s' %
                       (launcher.Platform().BriefPlatformName(),
                        sdk_version))
    return sdk_env_setting


  def _RequirementProblem(self, message):
    """Prerequisites are not available; warn user."""
    logging.warning(message)

  def DevAppServerCommand(self, project, extra_flags=None, verify=True):
    """Build a command for running dev_appserver.py with the project.

    Args:
      project: the launcher.Project we want to run.
      extra_flags: List of extra command line flags to add to this command.
      verify: if True, verify paths exist.  Only False in unit tests.
    Returns:
      A tuple of executable and args suitable for passing to subprocess.Popen().
    Raises:
      RuntimeException: Problem validating the run command (e.g. no python).
    """
    python_path = self._preferences[launcher.Preferences.PREF_PYTHON]
    my_sdkroot = self._preferences[launcher.Preferences.PREF_APPENGINE]
    if verify:
      if not (python_path and os.path.exists(python_path)):
        raise RuntimeException('Python interpreter %s not found.' % python_path)
      if not my_sdkroot:
        raise RuntimeException('App Engine SDK %s not found.' % my_sdkroot)
    dev_appserver = os.path.join(my_sdkroot, 'dev_appserver.py')
    if verify and not os.path.exists(dev_appserver):
        raise RuntimeException('App Engine program %s not found.' %
                               dev_appserver)
    command = ([python_path,
                dev_appserver,
               '--admin_console_server=',
               '--port=%s' % project.port] +
               project.flags +
               (extra_flags or []) +
               [project.path])
    return command

  def DeployCommand(self, project, authname, server=None):
    """Build a command for deploying (to Google) the project.

    Args:
      project: the launcher.Project we want to run.
      authname: the authorization name (e.g. fred@gmail.com)
      server: the server to deploy to.  If None, do not specify one
        explicitly on the command line.

    Returns:
      A tuple of executable and args suitable for passing to subprocess.Popen().
      On error (e.g. no SDK root), return None.
    """
    python_path = self._preferences[launcher.Preferences.PREF_PYTHON]
    sdk_root_path = self._preferences[launcher.Preferences.PREF_APPENGINE]
    if not python_path or not sdk_root_path:
      return None
    command = [python_path,
               os.path.join(sdk_root_path, 'appcfg.py'),
               '--no_cookies',
               '--email=%s' % authname,
               '--passin']
    if server:
      command.append('--server=%s' % server)
    command += ('update', project.path)
    return command
