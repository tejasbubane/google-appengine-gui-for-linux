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
"""Unittests for platform.py."""


import mox
import os
import subprocess
import sys
import unittest
import launcher

class PlatformTest(unittest.TestCase):
  """Unit test of platform.py.

  Almost by definition, platform.py will have low unit test coverage.
  """

  def setUp(self):
    self.platform = launcher.Platform()

  def tearDown(self):
    self.platform = None

  def testSingleton(self):
    p1 = launcher.Platform()
    p2 = launcher.Platform()
    self.assertEqual(id(self.platform), id(p1))
    self.assertEqual(id(p1), id(p2))

  def testPath(self):
    self.assertTrue(self.platform._FindInPath('cmd.exe') or
                    self.platform._FindInPath('sh'))
    self.assertTrue(self.platform._FindInPath('find.exe') or
                    self.platform._FindInPath('find'))
    self.assertFalse(self.platform._FindInPath('notFoundBLAH023030i3.exe'))

  def testKillProcess(self):
    cmd = (sys.executable, '-c', 'import time; time.sleep(20)')
    self.platform.KillProcess(subprocess.Popen(cmd))

  def testPythonCommand(self):
    self.assertTrue(os.path.exists(self.platform.PythonCommand()))

  def testAppEngineBaseDirectory(self):
    dirname = self.platform.AppEngineBaseDirectory()
    if dirname:
      # Requires appengine to be installed for dir to be found.
      self.assertTrue(os.path.exists(dirname))

  def _GenericTestConfigFile(self, filename):
    """Shared test code for configuration files."""
    if os.name != 'nt':
      self.assertTrue(os.path.exists(os.path.dirname(filename)))
    else:
      # There is no guarantee the parent directory exists on Windows
      # if make_parent_directory=False, so this is the best we can do.
      grandparent_dir = os.path.dirname(os.path.dirname(filename))
      self.assertTrue(grandparent_dir)

  def testPreferencesFile(self):
    self._GenericTestConfigFile(
        self.platform.PreferencesFile(make_parent_directory=False))

  def testProjectsFile(self):
    self._GenericTestConfigFile(self.platform.ProjectsFile
                                (make_parent_directory=False))

  def testOpenCommand(self):
    path = '/tmp/oops'
    cmd = self.platform.OpenCommand(path)
    if cmd:  # not implemented on Linux
      self.assertTrue(path in cmd)
      self.assertTrue(cmd[0] != path)
      self.assertTrue(os.path.exists(cmd[0]))

  def testBriefPlatformName(self):
    name = self.platform.BriefPlatformName()
    self.assertTrue(len(name) > 1)
    self.assertTrue(len(name) < 16)  # is that "short"?

  def testSuccessfulCommandResultCode(self):
    # Zero is always a successful result.
    self.assertTrue(self.platform.IsSuccessfulCommandResultCode(0))
    # These result codes are unsuccessful on all platforms.
    for code in (-180, 1, 42):
      self.assertFalse(self.platform.IsSuccessfulCommandResultCode(code))
    # Other successful result codes are platform dependent, so discriminate
    # based on the type of the platform object.
    if isinstance(self.platform, launcher.PlatformPosix):
      self.assertTrue(self.platform.IsSuccessfulCommandResultCode(-15))
    if isinstance(self.platform, launcher.PlatformWin):
      self.assertTrue(self.platform.IsSuccessfulCommandResultCode(-1))

  def testEdit(self):
    editor = self.platform.DefaultEditor()
    self.assertTrue(editor)
    cmd = self.platform.EditCommand(editor, 'foo')
    self.assertTrue(type(cmd) == list or type(cmd) == tuple)


class LinuxPlatformTest(unittest.TestCase):
  """Unit test of the Linux platform.

  If necessary, emulate linux environment.
  """

  def setUp(self):
    """Set up framework.

    Emulates Linux by forcing the linux path separator and setting a
    simplified path.
    """
    # Make like linux.
    self.original_sep = os.sep
    os.sep = '/'

    # Clone environment.
    self.original_environ = os.environ
    os.environ = dict(os.environ)
    os.environ['PATH'] = '/programs'

  def tearDown(self):
    """Restore original separator and environment."""
    os.sep = self.original_sep
    os.environ = self.original_environ

  def doOpenCommandTest(self, session, gnome_bin, kde_bin, expect):
    """Run the open command test.

    Args:
      session: Session that user is using.  None will clear the session
        environment variable.
      gnome_bin: Whether or not to emulate a gnome-open binary being
        installed on the system (in the fake path).
      kde_bin: Whether or not to emulate a konqueror binary being
        installed on the system (in the fake path).
      expect: Binary expected to use for opening.  None indicates that files
        cannot be opened (no gnome or kde binary installed) and OpenCommand
        should return None.
    """
    # Need to use a new mox no matter what.
    mox_instance = mox.Mox()
    exists = mox_instance.CreateMockAnything()

    linux = launcher.platform.PlatformLinux(exists=exists)
    exists(os.path.join('/programs/gnome-open')).AndReturn(gnome_bin)
    exists(os.path.join('/programs/konqueror')).AndReturn(kde_bin)

    if session is None:
      try:
        os.environ['DESKTOP_SESSION']
      except AttributeError:
        pass
    else:
      os.environ['DESKTOP_SESSION'] = session

    mox_instance.ReplayAll()

    if expect is None:
      self.assertEquals(None, linux.OpenCommand('/my/path'))
    else:
      self.assertEquals(('/programs/%s' % expect, '/my/path'),
                        linux.OpenCommand('/my/path'))

    mox_instance.VerifyAll()

  def testOpenCommandGnome(self):
    """Run the permuation of user configurations with OpenCommand."""
    for params in (
        # Session   gnome  kde    expected
        ('gnome',   True,  True,  'gnome-open'),
        ('gnome',   True,  False, 'gnome-open'),
        ('gnome',   False, True,  'konqueror'),
        ('gnome',   False, False, None),
        ('kde',     True,  True,  'konqueror'),
        ('kde',     True,  False, 'gnome-open'),
        ('kde',     False, True,  'konqueror'),
        ('kde',     False, False, None),
        ('unknown', True,  True,  'gnome-open'),
        ('unknown', True,  False, 'gnome-open'),
        ('unknown', False, True,  'konqueror'),
        ('unknown', False, False, None),
        (None,      True,  True,  'gnome-open'),
        (None,      True,  False, 'gnome-open'),
        (None,      False, True,  'konqueror'),
        (None,      False, False, None),
        ):
      self.doOpenCommandTest(*params)


if __name__ == '__main__':
  unittest.main()
