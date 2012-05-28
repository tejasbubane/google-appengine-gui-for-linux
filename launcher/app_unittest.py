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

"""Unittests for app.py."""

import os
import unittest
import launcher


class NoShowApp(launcher.App):

  def __init__(self):
    super(NoShowApp, self).__init__()
    self.displayed = False

  def _DisplayMainFrame(self):
    """Override so we don't actually display UI.

    Can't override by setting app._DisplayMainFrame to a new value
    since this gets hit before we have a chance to override.
    """
    self.displayed = True

  def _InitializeLogging(self):
    """Override so logs don't throw up modal dialogs."""
    pass


class NoShowNoVersionCheckApp(NoShowApp):

  def _VersionCheck(self, url=None):
    pass


class AppTest(unittest.TestCase):

  def testOnInit(self):
    app = NoShowNoVersionCheckApp()
    self.assertTrue(app.Initialized())

  def testVersionCheck(self):
    app = NoShowApp()
    warned = [False]
    def fakeNewVersionNeeded(a, b, c):
      warned[0] = True
    app._NewVersionNeeded = fakeNewVersionNeeded
    badurl = 'file://' + os.path.join(os.getcwd(),
                                      launcher.__path__[0],
                                      'app_unittest.py')
    # silent unhappy on purpose
    app._VersionCheck(badurl)
    self.assertEqual(False, warned[0])

    def DumpAndVersionCheck(data, app):
      filename = os.tempnam()
      f = open(filename, 'w')
      f.write(data)
      f.close()
      app._VersionCheck('file:///' + filename)
      return filename

    # try hard to look like we're out of date
    new_version_file = ('release: "9999.9999.9999"\n' +
                        'timestamp: 9999999999\n' +
                        'api_versions: [\'1\']\n')
    self.assertEqual(False, warned[0])
    filename = DumpAndVersionCheck(new_version_file, app)
    os.unlink(filename)
    self.assertEqual(True, warned[0])
    warned[0] = False

    # Make sure we are NOT out of date
    old_version_file = ('release: "0.0.0"\n' +
                        'timestamp: 7\n' +
                        'api_versions: [\'1\']\n')
    self.assertEqual(False, warned[0])
    filename = DumpAndVersionCheck(old_version_file, app)
    os.unlink(filename)
    self.assertEqual(False, warned[0])


    # VERSION file or well-defined failure string
    # (depends on prefs setting...)
    current = app._CurrentVersionData()
    self.assertTrue('api_version' in current)


if __name__ == '__main__':
  unittest.main()
