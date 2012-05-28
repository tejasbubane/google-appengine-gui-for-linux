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
"""Unittests for preferences.py"""

import unittest
import tempfile
import mox
import wx
import launcher


class PreferencesTest(unittest.TestCase):

  class FakePlatform(object):

    def PythonCommand(self):
      return 'super-python'

    def AppEngineBaseDirectory(self):
      return 'aebd'

    def DefaultEditor(self):
      for path in ('/bin/ls', 'C:/WINDOWS'):
        if os.path.exists(path):
          return path
      return 'oops'


  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()
    # We just want temp filename.  On Windows, we need to close it
    # before permissions will let us reuse the name.  Other
    # temp-filename-but-no-filedesc routines throw warnings.
    self.file = tempfile.NamedTemporaryFile()
    self.filename = self.file.name
    self.file.close()
    self._problem = False
    self.saved_preferences = None

  def tearDown(self):
    if self.saved_preferences:
      self.assertFalse(self._problem)

  def preferences(self):
    p = launcher.Preferences(self.filename)
    p._PreferenceProblem = self._PreferenceProblem
    self.saved_preferences = p
    return p

  def _PreferenceProblem(self, str):
    """Override of Preferences method so we know it was called"""
    self._problem = True

  def testBasics(self):
    # I know "tmpnam is a potential security risk to your program", but
    # I need a filename, and os.tmpfile() doesn't give me one.
    # Test empty prefs on creation
    p = self.preferences()
    self.assertFalse(p.Items())
    # Add an item and save it
    p['key'] = 'value'
    self.assertEqual('value', p['key'])
    p.Save()
    # New prefs with the same filename; make sure we see the same thing
    nextp = launcher.Preferences(self.filename)
    self.assertTrue(nextp.Items())
    self.assertEqual('value', nextp['key'])
    nextp['new'] = 'new'
    # Make sure the 1st prefs doesn't see it until it's saved/reloaded
    self.assertFalse(p['new'])
    nextp.Save()
    self.assertFalse(p['new'])
    p.Load()
    self.assertEqual('new', p['new'])

  def testLots(self):
    p = self.preferences()
    self.assertFalse(p.Items())
    for i in range(300):
      key = 'SuperKey-%d' % i
      value = 'SuperMonsterValue-%d-ooh-yeah' % (i*10)
      self.assertFalse(p[key])
      p.Set(key, value)
    self.assertEqual(300, len(p.Items()))
    p.Save()
    self.assertEqual(300, len(p.Items()))

  def testBadFile(self):
    p = launcher.Preferences('/this_path_does_not_exist/bin_denial_factory')
    self._problem = False
    p._PreferenceProblem = self._PreferenceProblem
    p.Save()
    self.assertTrue(self._problem)

  def testGetVsDefault(self):
    p = launcher.Preferences('/foo', self.FakePlatform())
    p.Set(launcher.Preferences.PREF_PYTHON, 'clown-shoes')
    self.assertEqual('clown-shoes', p.Get(launcher.Preferences.PREF_PYTHON))
    self.assertEqual('super-python',
                     p.GetDefault(launcher.Preferences.PREF_PYTHON))
    self.assertEqual(p[launcher.Preferences.PREF_PYTHON],
                     p.Get(launcher.Preferences.PREF_PYTHON))

  def testDefaultEditor(self):
    p = launcher.Preferences('/foo', launcher.Platform())
    editor = p.GetDefault(launcher.Preferences.PREF_EDITOR)
    self.assertTrue(os.path.exists(editor))


if __name__ == '__main__':
  unittest.main()
