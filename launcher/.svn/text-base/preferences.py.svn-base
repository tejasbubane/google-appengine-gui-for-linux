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
import ConfigParser
import wx
import launcher


class Preferences(object):
  """Configuration params for wxLauncher.

  Preferences are stored in an INI file (RFC822) so they are human
  readable.  The preference file is either
  ~/.google_app_engine_prefs.ini (POSIX) or C:\"Documents and Settings\
    username\Application Data\Google\Preferences.ini
  An example preference is the path to the python you wish to use for
  running the dev_appserver.
  """

  # Well-defined preference names.  Arbitrary names can exist in our
  # preference file but aren't treated specially (no UI for them in
  # the Preference dialog, no documentation, etc)
  # These preferences are in the Preference panel:
  PREF_PYTHON = 'python'
  PREF_APPENGINE = 'appengine'
  PREF_DEPLOY_SERVER = 'deploy_server'
  PREF_EDITOR = 'editor'
  # And these are not:
  PREF_MAIN_WINDOW_RECT = 'mainwindowrect'
  PREF_NOVERSIONCHECK = 'noversioncheck'

  # ConfigParser section for prefs
  _PREF_SECTION = 'preferences'

  def __init__(self, filename=None, platform=None):
    """Initialize our Preferences object.

    Args:
      filename: the preference filename.
        If None, use a platform-specific default.
      platform: a platform object.  Default is None.
    """
    self._platform = platform or launcher.Platform()
    self._filename = filename or self._platform.PreferencesFile()
    self._parser = ConfigParser.ConfigParser()
    self._pref_defaults = {
        self.PREF_PYTHON: self._platform.PythonCommand(),
        self.PREF_APPENGINE: self._platform.AppEngineBaseDirectory(),
        self.PREF_DEPLOY_SERVER: None,
        self.PREF_EDITOR: self._platform.DefaultEditor(),
        self.PREF_NOVERSIONCHECK: None,
    }
    self.Load()

  def Load(self):
    """Load (or reload) preferences from our preference file."""
    self._parser.read([self._filename])
    # Make sure we have our special section
    if not self._parser.has_section(self._PREF_SECTION):
      self._parser.add_section(self._PREF_SECTION)

  def Save(self):
    """Save preferences into our preference file."""
    # First clean out preferences which don't look useful.
    # For example, a python path of "" means you probably
    # didn't intend to override the default value.
    optionlist = self._parser.options(self._PREF_SECTION)
    for option in optionlist:
      value = self._parser.get(self._PREF_SECTION, option)
      if not value.strip():
        self._parser.remove_option(self._PREF_SECTION, option)
    # Then save them to disk.
    try:
      fp = file(self._filename, 'w')
      fp.write('# Google App Engine Launcher preferences\n')
      fp.write('# http://code.google.com/appengine\n')
      self._parser.write(fp)
      fp.close()
    except IOError, err:
      (errno, strerror) = err
      self._PreferenceProblem('Could not save into preference file %s: %s' %
                             (self._filename, strerror))
    pass

  # Expose a dictionary-like get interface for convenience
  def __getitem__(self, key):
    """Try and return a reasonable value for the given preference key.

    Args:
      key: the preference name we are looking for
    Returns:
      The preference setting (if found), or a default value.
    """
    return self.Get(key) or self.GetDefault(key)

  # Expose a dictionary-like set interface for convenience
  def __setitem__(self, key, value):
    return self.Set(key, value)

  def Get(self, key):
    """Return the preference value for the input key, or None.

    This method does NOT default to a default value.

    Args:
      key: the preference name we are looking for.
    Returns:
      The preference setting (if found), or None.
    """
    if self._parser.has_option(self._PREF_SECTION, key):
      return self._parser.get(self._PREF_SECTION, key)
    return None

  def GetDefault(self, key):
    """Get the default for the preference.

    This metnod does not check actual preference settings.

    Args:
      key: The preference we are looking for.
    Returns:
      The default value for the given preference, or None.
    """
    return self._pref_defaults.get(key, None)

  def Set(self, key, value):
    """Set a preference value for the input key."""
    self._parser.set(self._PREF_SECTION, key, value)

  def Items(self):
    """Return a list of tuples with (name, value) for each option."""
    return self._parser.items(self._PREF_SECTION)

  def _PreferenceProblem(self, str):
    """We had a problem saving preferences; tell the user."""
    logging.warning(str)
