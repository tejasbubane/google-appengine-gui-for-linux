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

"""Unittests for maintable.py"""

import os
import tempfile
import unittest
import wx
import launcher


class MainTableTest(unittest.TestCase):

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()

    # Make a temporary (empty) file so that MainTable doesn't abuse the
    # user's real project configuration file.
    temp_fd, self._temp_filename = tempfile.mkstemp(text=True)
    os.close(temp_fd)

  def tearDown(self):
    os.remove(self._temp_filename)

  def checkProject(self, project, path, name, port):
    """Make sure a project's attributes match what's expected."""
    self.assertEqual(path, project.path)
    self.assertEqual(name, project.name)
    self.assertEqual(port, project.port)

  def testEmptyTable(self):
    table = launcher.MainTable(self._temp_filename)
    self.assertEqual(0, table.ProjectCount())

  def testProjects(self):
    table = launcher.MainTable(self._temp_filename)
    projects = []
    for i in range(20):
      projects.append(launcher.Project('/tmp/himom'+str(i), 8000+i))
    # test Add/Remove
    for p in projects:
      table.AddProject(p)
      self.assertEqual(p, table.ProjectAtIndex(0))
      table.RemoveProject(p)
    # Test big table and extraction
    for p in projects:
      table.AddProject(p)
    self.assertEqual(projects[19], table.ProjectAtIndex(19))
    self.assertEqual(projects[12], table.ProjectAtIndex(12))
    self.assertTrue(table.ProjectCount() >= 20)
    # Test indexing off the end, which should return None
    self.assertEqual(None, table.ProjectAtIndex(2817372))

  def testFileLoading(self):
    # Reach in and get the projects array and make sure it has the
    # expected projects in the correct order.

    table = launcher.MainTable('launcher/testdata/project1.ini')
    self.assertEqual(4, table.ProjectCount())

    self.checkProject(table.ProjectAtIndex(0),'/tmp', 'ook', 8180)
    self.checkProject(table.ProjectAtIndex(1), '/tmp/path with spaces/bar',
                      'baz', 8110)
    self.checkProject(table.ProjectAtIndex(2),
                      '/tmp/himom0 with spaces', 'himom0 with spaces', 8000)

  def testFileSaving(self):
    # Make a temp file, and have the table save its projects there.
    table = launcher.MainTable(self._temp_filename)

    project = launcher.Project('/hurdy/gurdy/bonnie', 1910)
    table.AddProject(project)

    project = launcher.Project('/Users/bork/kim', 1975)
    table.AddProject(project)

    project = launcher.Project('/annie', 1860)
    table.AddProject(project)

    # Make sure paths with spaces are OK.
    project = launcher.Project('/ekky/ek ky/ekky/ek ky', 1967)
    table.AddProject(project)

    # It's valid to have multiple projects with the same name.
    project = launcher.Project('/little/orphan/annie', 1924)
    table.AddProject(project)

    # And for there to be duplicates.
    project = launcher.Project('/little/orphan/annie', 1924)
    table.AddProject(project)

    # Make another table, pointed at that file, and make sure everything
    # comes back that should.

    table2 = launcher.MainTable(self._temp_filename)
    # Reach in and get the projects array and make sure it has the
    # expected projects in the correct order.
    self.assertEqual(6, table.ProjectCount())

    self.checkProject(table.ProjectAtIndex(0), '/hurdy/gurdy/bonnie', 'bonnie', 1910)
    self.checkProject(table.ProjectAtIndex(1), '/Users/bork/kim', 'kim', 1975)
    self.checkProject(table.ProjectAtIndex(2), '/annie', 'annie', 1860)
    self.checkProject(table.ProjectAtIndex(3), '/ekky/ek ky/ekky/ek ky',
                      'ek ky', 1967)
    self.checkProject(table.ProjectAtIndex(4), '/little/orphan/annie', 'annie', 1924)
    self.checkProject(table.ProjectAtIndex(5), '/little/orphan/annie', 'annie', 1924)

  def testUniquePort(self):
    table = launcher.MainTable(self._temp_filename)
    self.assertTrue(table.UniquePort() > 1024)
    ports = range(8000, 8020) + range(8021, 8200, 17)
    for i in range(len(ports)):
      table.AddProject(launcher.Project('/tmp/himom'+str(i), ports[i]))
      unused = table.UniquePort()
      self.assertTrue(unused not in ports[:i+1])
      self.assertTrue(unused > 1024)


if __name__ == '__main__':
  unittest.main()
