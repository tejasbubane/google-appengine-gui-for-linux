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

"""Unittests for runtime.py"""

import os
import unittest
import tempfile
import mox
import launcher


class FakePlatform(object):
  """Fake launcher.Platform"""

  def __init__(self, python, basedir):
    self._python = python
    self._basedir = basedir

  def PythonCommand(self):
    return self._python

  def AppEngineBaseDirectory(self):
    return self._basedir

  def DefaultEditor(self):
    return 'blah'

class RuntimeNoDialog(launcher.Runtime):
  """A launcher.Runtime which sets a flag instead of throwing up a dialog."""

  def __init__(self, platform=None, preferences=None):
    """Odd args for historical reasons."""
    self.problem = False
    preferences = preferences or launcher.Preferences(platform=platform)
    super(RuntimeNoDialog,self).__init__(preferences)

  def _RequirementProblem(self, message):
    self.problem = True

class RuntimeTest(unittest.TestCase):

  def setUp(self):
    # We just want temp filename.  On Windows, we need to close it
    # before permissions will let us reuse the name.  Other
    # temp-filename-but-no-filedesc routines throw warnings.
    self.file = tempfile.NamedTemporaryFile()
    self.filename = self.file.name
    self.file.close()

  def testSetThenGet(self):
    platform = FakePlatform('pythoncmd', 'dir')
    pref = launcher.Preferences(self.filename, platform)
    runtime = RuntimeNoDialog(platform, pref)
    self.assertFalse(runtime.problem)
    project = launcher.Project('super-path', '123', False)
    das = runtime.DevAppServerCommand(project, verify=False)
    self.assertTrue('pythoncmd' in das)
    self.assertTrue('photojournalist' not in das)
    pref[launcher.Preferences.PREF_PYTHON] = 'photojournalist'
    das = runtime.DevAppServerCommand(project, verify=False)
    self.assertTrue('pythoncmd' not in das)
    self.assertTrue('photojournalist' in das)
    self.assertRaises(launcher.RuntimeException,
                      runtime.DevAppServerCommand,
                      project)

  def testBadDefaults(self):
    """Pass in None for some defaults with no pref overrides."""
    runtime = RuntimeNoDialog(None,
                              launcher.Preferences(self.filename,
                                                   FakePlatform(None, None)))
    self.assertTrue(runtime.problem)
    runtime = RuntimeNoDialog(None,
                              launcher.Preferences(self.filename,
                                                   FakePlatform(None, 'hi')))
    self.assertTrue(runtime.problem)
    runtime = RuntimeNoDialog(None,
                              launcher.Preferences(self.filename,
                                                   FakePlatform('hi', None)))
    self.assertTrue(runtime.problem)

  def testNoDefaultsAllPrefsOverride(self):
    """None for ALL defaults, all pref overrides, and make sure all is happy."""
    pref = launcher.Preferences(self.filename, FakePlatform(None, None))
    pycmd = '/usr/bin/python'
    pref[launcher.Preferences.PREF_PYTHON] = pycmd
    pref[launcher.Preferences.PREF_APPENGINE] = '/tmp/foo/bar/baz'
    runtime = RuntimeNoDialog(preferences=pref)
    self.assertFalse(runtime.problem)
    project = launcher.Project('super-path', '123')

    # test of DevAppServerCommand()
    das = runtime.DevAppServerCommand(project, verify=False)
    self.assertTrue(pycmd in das)
    self.assertTrue('super-path' in das)
    self.assertTrue('--port=123' in das)
    self.assertFalse('--mega-flag' in das)
    self.assertRaises(launcher.RuntimeException,
                      runtime.DevAppServerCommand,
                      project, verify=True)

    # test project flags
    project.flags = ['--mega-flag', '--oops']
    das = runtime.DevAppServerCommand(project, verify=False)
    self.assertTrue('--mega-flag' in das)
    self.assertTrue('--oops' in das)

    # test DevAppServerCommand's extra_flags
    extras = ['--hammertime', '--singsong']
    for flag in extras:
      self.assertFalse(flag in das)
    das = runtime.DevAppServerCommand(project, extra_flags=extras, verify=False)
    for flag in extras:
      self.assertTrue(flag in das)

    # test of DeployCommand()
    deploy_cmd = runtime.DeployCommand(project, 'evil@badguy.com')
    for s in (pycmd, '--email=evil@badguy.com', 'update', 'super-path'):
      self.assertTrue(s in deploy_cmd)
    deploy_cmd = runtime.DeployCommand(project, 'evil@badguy.com', 'xazzy')
    self.assertTrue('--server=xazzy' in deploy_cmd)

  def testGetSDKEnvironmentSetting(self):
    pref = launcher.Preferences(self.filename, platform=launcher.Platform())
    runtime = RuntimeNoDialog(preferences=pref)
    sdk_env = runtime._GetSDKEnvironmentSetting()
    self.assertTrue('-launcher-' in sdk_env)
    self.assertTrue('\n' not in sdk_env)


if __name__ == '__main__':
  unittest.main()
