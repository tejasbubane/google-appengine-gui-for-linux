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

"""Unittests for addnew_controller.py."""


import os
import shutil
import tempfile
import unittest
import wx
import launcher


class AddNewControllerTest(unittest.TestCase):
  """Unit test case for AddNewController."""

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()
    self.tempdir = None

  def tearDown(self):
    if self.tempdir:
      shutil.rmtree(self.tempdir)

  def testBasics(self):
    anc = launcher.AddNewController()
    self.assertTrue(os.path.exists(anc.GetPath()))
    self.assertFalse(os.path.exists(os.path.join(anc.GetPath(),
                                                 anc.GetName())))
    # Implies SDK installed
    self.assertTrue(anc._NewProjectTemplate())

  def testNewProjectNameInDirectory(self):
    """Also test _SanityCheckPathDoesNotExist."""
    anc = launcher.AddNewController()
    def MarkFailure(msg, capt):
      pass
    anc.FailureMessage = MarkFailure
    self.tempdir = tempfile.mkdtemp()
    for counter in range(3):
      name = anc._NewProjectNameInDirectory(self.tempdir)
      fullnewpath = os.path.join(self.tempdir, name)
      self.assertFalse(os.path.exists(fullnewpath))
      self.assertTrue(anc._SanityCheckPathDoesNotExist(fullnewpath))
      os.mkdir(fullnewpath)
      self.assertFalse(anc._SanityCheckPathDoesNotExist(fullnewpath))

  def testGetSetName(self):
    anc = launcher.AddNewController()
    for name in ('hi', 'mom', 'howAREyouTODAYfineKTHXbye', ''):
      anc.SetName(name)
      self.assertEqual(anc.GetName(), name)

  def testSanityName(self):
    anc = launcher.AddNewController()
    def MarkFailure(msg, capt):
      pass
    anc.FailureMessage = MarkFailure
    for name in ('hi', 'howAREyouTODAYfineKTHXbye'):
      self.assertTrue(anc._SanityCheckName(name))
    for name in ('', None):
      self.assertFalse(anc._SanityCheckName(name))

  def testNoSDK(self):
    anc = launcher.AddNewController()
    failures = [0]
    # Count failures
    def CountFailures(msg, capt):
      failures[0] += 1
    anc.FailureMessage = CountFailures
    preferences = { launcher.Preferences.PREF_APPENGINE: None }
    templatedir = anc._NewProjectTemplate(preferences=preferences)
    self.assertEqual(1, failures[0])

  def testCreateProjectOnDisk(self):
    anc = launcher.AddNewController()
    anc.SetPort(8000)
    self.tempdir = tempfile.mkdtemp()
    templatedir = os.path.join(self.tempdir, 'template')
    os.mkdir(templatedir)
    appyaml = os.path.join(templatedir, 'app.yaml')
    f = file(appyaml, 'w')
    f.write('application: new-project-template')
    f.close()
    def NewProjectTemplate():
      return templatedir
    anc._NewProjectTemplate = NewProjectTemplate
    newpath = os.path.join(self.tempdir, 'yippie')
    self.assertTrue(anc._CreateProjectOnDisk(newpath, 'yippie'))
    newyaml = os.path.join(newpath, 'app.yaml')
    self.assertTrue(os.path.exists(newyaml))
    line = open(newyaml, 'r').readline()
    # Warning: string.find() can return 0 for 'match at index 0'
    # which is a successful match.
    self.assertTrue(line.find('yippie'))

  def testProject(self):
    anc = launcher.AddNewController()
    def MarkFailure(msg, capt):
      pass
    anc.FailureMessage = MarkFailure
    self.assertFalse(anc.Project())
    anc._dialog_return_value = wx.ID_OK
    self.assertFalse(anc.Project())
    self.tempdir = tempfile.mkdtemp()
    anc.SetPath(self.tempdir)
    self.assertFalse(anc.Project())
    anc.SetPort(8000)
    name = 'blah'
    anc.SetName(name)
    created = [False]
    def CreateProjectOnDisk(newpath, name):
      created[0] = True
      return True
    anc._CreateProjectOnDisk = CreateProjectOnDisk
    self.assertTrue(anc.Project())
    self.assertTrue(created[0])
    os.mkdir(os.path.join(self.tempdir, name))
    created[0] = False
    self.assertFalse(anc.Project())
    self.assertFalse(created[0])

if __name__ == '__main__':
  unittest.main()
