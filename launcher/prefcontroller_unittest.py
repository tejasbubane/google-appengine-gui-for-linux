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
"""Unittests for prefcontroller.py."""


import unittest
import mox
import wx
import launcher


# A mox would be convenient but I found it difficult to allow "any
# args" to a mock method.

class FakeController(launcher.PrefController):
  """A PrefController with _BuildPreferenceViews nooped."""

  def __init__(self, prefs, view):
    super(FakeController, self).__init__(prefs, view)

  def _BuildPreferenceViews(self):
    # intentionally empty
    pass


class PrefControllerTest(unittest.TestCase):
  """Unit test case for PrefController."""

  class FakePrefs(object):

    def __init__(self):
      self._prefs = {
          launcher.Preferences.PREF_PYTHON: None,
          launcher.Preferences.PREF_APPENGINE: None,
          launcher.Preferences.PREF_DEPLOY_SERVER: None,
          launcher.Preferences.PREF_EDITOR: None,
      }

    def __getitem__(self, key):
      return self._prefs[key]

    def __setitem__(self, key, value):
      self._prefs[key] = value

    Get = __getitem__
    GetDefault = __getitem__


  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()
    self.prefs = self.FakePrefs()

  def returnFalse(self):
    return False

  def testConstruct(self):
    pc = launcher.PrefController(self.prefs)
    pc._CreatePreferenceDialog()
    self.assertTrue(pc.PreferenceCount() == 0)
    pc._ShowDialogModally = self.returnFalse
    pc._DestroyPreferenceDialog = self.returnFalse
    pc.ShowModal()
    self.assertTrue(pc.PreferenceCount() > 0)
    pass

  def testCancel(self):
    """Dialog comes up but is then cancelled."""
    dialog_mock = mox.MockObject(launcher.PreferenceView)
    dialog_mock.ShowModal().AndReturn(wx.ID_CANCEL)
    dialog_mock.Destroy()
    mox.Replay(dialog_mock)
    pc = FakeController(self.prefs, dialog_mock)
    pc.ShowModal()
    mox.Verify(dialog_mock)

  def testOK(self):
    """Dialog comes up and a change is made."""
    dialog_mock = mox.MockObject(launcher.PreferenceView)
    dialog_mock.ShowModal().AndReturn(wx.ID_OK)
    python_pref = launcher.Preferences.PREF_PYTHON
    appengine_pref = launcher.Preferences.PREF_APPENGINE
    deploy_pref = launcher.Preferences.PREF_DEPLOY_SERVER
    editor_pref = launcher.Preferences.PREF_EDITOR
    dialog_mock.Get(python_pref).InAnyOrder().AndReturn('python-2')
    dialog_mock.Get(appengine_pref).InAnyOrder().AndReturn(None)
    dialog_mock.Get(deploy_pref).InAnyOrder().AndReturn(None)
    dialog_mock.Get(editor_pref).InAnyOrder().AndReturn(None)
    dialog_mock.Destroy()
    mox.Replay(dialog_mock)
    pc = FakeController(self.prefs, dialog_mock)
    pc.ShowModal()
    mox.Verify(dialog_mock)
    self.assertEqual('python-2', self.prefs[python_pref])


if __name__ == '__main__':
  unittest.main()
