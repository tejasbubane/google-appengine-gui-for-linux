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

import wx
import launcher


class PrefController(object):
  """Controller for preferences (M)."""

  def __init__(self, prefs, view=None):
    """Initialize a PrefController.

    Args:
      prefs: the Preferences object.
      view: the preference view (dialog) to use.
        If None, one is created when needed.
        Likely only set in a unit test.
    """
    super(PrefController, self).__init__()
    self._preferences = prefs
    self._dialog = view

  def ShowModal(self):
    """Show a modal dialog that displays the current preferences.

    When the dialog is done, we read it's values and set preferences.
    These preference changes are saved to disk.
    """
    self._CreatePreferenceDialog()
    self._BuildPreferenceViews()
    if self._ShowDialogModally():
      self._ProcessNewPreferences()
    self._DestroyPreferenceDialog()

  def PreferenceCount(self):
    """Return the number of preferences displayed by the dialog."""
    if not self._dialog:
      return 0
    return self._dialog.PreferenceCount()

  def _CreatePreferenceDialog(self):
    if not self._dialog:
      self._dialog = launcher.PreferenceView()

  def _BuildPreferenceViews(self):
    """Add appropriate content to our preference dialog."""
    # TODO(jrg): find a centralized way to determine defaults
    #   (if prefs not set), and discuss them in the description.
    #   Currently defaults (for these two) are embedded in runtime.py.
    # TODO(jrg): a little mixing of M, V, and C here?
    pref_python = self._preferences.Get(launcher.Preferences.PREF_PYTHON)
    def_python = self._preferences.GetDefault(launcher.Preferences.PREF_PYTHON)
    self._dialog.Append(launcher.Preferences.PREF_PYTHON,
                        summary='Python Path',
                        description='A path to a python executable.',
                        file_selector=True,
                        value=pref_python,
                        default=def_python)
    sdk_desc = ('A path to the root of the Google App Engine SDK.\n'
                r'Example: "C:\Program Files\Google\google_appengine"')
    pref_appengine = self._preferences.Get(launcher.Preferences.PREF_APPENGINE)
    def_appengine = self._preferences.GetDefault(launcher.Preferences.PREF_APPENGINE)
    self._dialog.Append(launcher.Preferences.PREF_APPENGINE,
                        summary='App Engine SDK',
                        description=sdk_desc,
                        dir_selector=True,
                        value=pref_appengine,
                        default=def_appengine)
    pref_editor = self._preferences.Get(launcher.Preferences.PREF_EDITOR)
    def_editor = self._preferences.GetDefault(launcher.Preferences.PREF_EDITOR)
    self._dialog.Append(launcher.Preferences.PREF_EDITOR,
                        summary='Editor',
                        description='Editor for Application files.',
                        file_selector=True,
                        value=pref_editor,
                        default=def_editor)
    deploy_desc = ('The server where this application will be deployed.\n'
                   'Most users should leave this as the default (unset).')
    deploy_pref_name = launcher.Preferences.PREF_DEPLOY_SERVER
    pref_deploy = self._preferences.Get(deploy_pref_name)
    def_deploy = self._preferences.GetDefault(deploy_pref_name)
    self._dialog.Append(deploy_pref_name,
                        summary='Deployment Server',
                        description=deploy_desc,
                        value=pref_deploy,
                        default=def_deploy)

  def _ShowDialogModally(self):
    """Run our preference dialog modally.  Returns False if dialog Cancelled."""
    rtn = self._dialog.ShowModal()
    if rtn == wx.ID_OK:
      return True
    return False

  def _ProcessNewPreferences(self):
    """Find and process modifications.

    If any modifications are found, set the appropriate preference and
    save preferences to disk (with a call to Preferences.Save().
    """
    modified = False
    for pref in (launcher.Preferences.PREF_PYTHON,
                 launcher.Preferences.PREF_APPENGINE,
                 launcher.Preferences.PREF_DEPLOY_SERVER,
                 launcher.Preferences.PREF_EDITOR):
      oldval = self._preferences.Get(pref)
      newval = self._dialog.Get(pref)
      if newval != oldval:
        modified = True
        self._preferences[pref] = newval
    # Use hasattr so we can subst a dict in here for unit tests
    if modified and hasattr(self._preferences, "Save"):
      self._preferences.Save()

  def _DestroyPreferenceDialog(self):
    """Destroy the wx dialog.

    When using wx we must explicitly destroy (dealloc) when done.
    """
    self._dialog.Destroy()
    self._dialog = None
