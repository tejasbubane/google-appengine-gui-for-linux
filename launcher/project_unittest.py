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

"""Unittests for project.py"""

import ConfigParser
import os
import shutil
import unittest
import launcher


class ProjectTest(unittest.TestCase):

  def setUp(self):
    self._temp_project = None

  def tearDown(self):
    if self._temp_project:
      self.deleteTempProject()

  def deleteTempProject(self):
    if self._temp_project:
      if not os.path.exists(os.path.join(self._temp_project, 'app.yaml')):
        print "I'm too scared to delete the directory " + self._temp_project
      else:
        shutil.rmtree(self._temp_project)
      self._temp_project = None

  def createYaml(self, name, dirname):
    """Write an app.yaml.

    Args:
      name: the project name
      dirname: directory to contain the app.yaml
    """
    yaml = 'application: %s\nversion: 1\nruntime: python\n\n' % name
    f = open(os.path.join(dirname, 'app.yaml'), 'w')
    f.write(yaml)
    f.close()

  def createTempProject(self, name):
    if self._temp_project:
      return
    dirname = os.tempnam()  # I know it's insecure; I'm OK with that.
    os.mkdir(dirname)
    self.createYaml(name, dirname)
    self._temp_project = dirname

  def checkProject(self, project, path, name, port, flags=None):
    """Make sure a project's attributes match what's expected."""
    self.assertEqual(path, project.path)
    self.assertEqual(name, project.name)
    self.assertEqual(port, project.port)
    self.assertEqual(flags or [], project.flags)

  def testProperties(self):
    for plist in (('foo', '/tmp/foo', 8000),
                  ('zzz', '/yo/momma/zzz', 9000)):
      p = launcher.Project(plist[1], plist[2])
      self.assertEqual(p.name, plist[0])
      self.assertEqual(p.path, plist[1])
      self.assertEqual(p.port, plist[2])

  def testEquality(self):
    p1 = launcher.Project('/tmp/foo', 8000)
    p2 = launcher.Project('/tmp/foo', 8001)
    p3 = launcher.Project('/windindicfnodsin', 8000)
    p4 = launcher.Project('/tmp/foo', 8000)

    self.assertEqual(p1, p4)  # same path and port
    self.assertNotEqual(p1, p2)  # differ by port
    self.assertNotEqual(p1, p3)  # differ by path
    self.assertNotEqual(p2, p3)  # differ by path and port
    # make sure both __eq__ and __ne__ hit; no guarantee with unittest
    self.assertTrue(p1 == p4)
    self.assertTrue(p1 != p3)
    # Make sure we test with "projects" that exist on disk
    for dir in ('/bin', 'c:\\'):
      self.assertEqual(launcher.Project(dir, 8010),
                       launcher.Project(dir, 8010))
      self.assertNotEqual(launcher.Project(dir, 8010),
                          launcher.Project(dir, 8011))

  def testPort(self):
    """Make sure we can't set the port while running."""
    p1 = launcher.Project('/tmp/foo', 8000)
    self.assertEqual(8000, p1.port)
    p1.port = 102
    self.assertEqual(102, p1.port)
    p1.runstate = launcher.Project.STATE_RUN
    def setPort():
      p1.port = 8000
    self.assertRaises(launcher.ProjectException, setPort)
    self.assertEqual(102, p1.port)
    p1.runstate = launcher.Project.STATE_STOP
    p1.port = 8001
    self.assertEqual(8001, p1.port)

  def testRunState(self):
    p1 = launcher.Project('/tmp/foo', 8000)
    for state in launcher.Project.ALL_STATES:
      p1.runstate = state
      self.assertEqual(state, p1.runstate)
    for state in ('hi mom', 1029333, None):
      def setRunState():
        p1.runstate = state
      self.assertRaises(launcher.ProjectException, setRunState)

  def testName(self):
    p = launcher.Project('/tmp/foo', 8000, 'my_name')
    self.assertEqual('my_name', p.name)
    # make sure we cannot set the name (hidden with @property)
    def setName():
      p.name = 'doh'
    self.assertRaises(AttributeError, setName)
    self.assertEqual('my_name', p.name)
    p = launcher.Project('/tmp/foo', 8000, name='bozo')
    self.assertEqual('bozo', p.name)

  def testSpaceRemoval(self):
    p = launcher.Project('   /tmp/foo ', 8000, ' my_name   ')
    self.assertEqual('/tmp/foo', p.path)
    self.assertEqual('my_name', p.name)

  def testFlags(self):
    p = launcher.Project('/tmp/foo', 8000)
    self.assertEqual([], p.flags)
    flags = ['--hi', '--mom']
    p = launcher.Project('/tmp/foo', 8000, name='name', flags=flags)
    self.assertEqual(flags, p.flags)

  def testNameFromAppYaml(self):
    name = 'squeaky_nose'
    self.createTempProject(name)
    p = launcher.Project(self._temp_project, 9000)
    self.assertEqual(p.name, name)

  def testVerifyAndValid(self):
    p = launcher.Project('/tmp/foo/smin/du7737g', 8000, 'name')
    self.assertFalse(p.valid)
    p.Verify()
    self.assertFalse(p.valid)
    self.createTempProject('turbo-monkey')
    p = launcher.Project(self._temp_project, 8000)
    self.assertTrue(p.valid)
    p.Verify()
    self.assertTrue(p.valid)
    self.deleteTempProject()
    p.Verify()
    self.assertFalse(p.valid)

  def testUpdateNameOnVerify(self):
    name = 'starting_name'
    self.createTempProject(name)
    p = launcher.Project(self._temp_project, 9000)
    self.assertEqual(name, p.name)
    name = 'ending_name'
    self.createYaml(name, self._temp_project)
    p.Verify()
    self.assertEqual(name, p.name)  # the new name

  def testInitParameters(self):
    # Make sure bad arguments raise.

    # None when there should be.
    self.assertRaises(launcher.ProjectException, launcher.Project, None, None)
    self.assertRaises(launcher.ProjectException, launcher.Project, 'bork', None)
    self.assertRaises(launcher.ProjectException, launcher.Project, None, 'bork')

    self.assertRaises(launcher.ProjectException,
                      launcher.Project.ProjectWithConfigParser, None, None)
    self.assertRaises(launcher.ProjectException,
                      launcher.Project.ProjectWithConfigParser, None, 'snook')
    self.assertRaises(launcher.ProjectException,
                      launcher.Project.ProjectWithConfigParser, 'hork', None)

  def testLoad(self):
    parser = ConfigParser.ConfigParser()
    ook = parser.read('launcher/testdata/project1.ini')

    p = launcher.Project.ProjectWithConfigParser(parser, '1')
    self.checkProject(p, '/tmp', 'ook', 8180)

    self.checkProject(launcher.Project.ProjectWithConfigParser(parser, '2'),
                      '/tmp/path with spaces/bar', 'baz', 8110)

    self.checkProject(launcher.Project.ProjectWithConfigParser(parser, '3'),
                      '/tmp/himom0 with spaces', 'himom0 with spaces', 8000)

    flags = ['--clowns-rule', '--clownpath=c:/Program Files']
    self.checkProject(launcher.Project.ProjectWithConfigParser(parser, '4'),
                      '/tmp/bozo', 'bozo', 8000, flags)

  def testStore(self):
    project = launcher.Project('/tmp/hoover', 8000)
    flagsproj = launcher.Project('/tmp/markd-attack', 8001,
                                 'run-for-your-life',
                                 flags=['--vehicular-assault'])

    # make some stuff, write it out, and re-load it
    parser = ConfigParser.ConfigParser()
    parser.add_section('greeble')
    parser.add_section('grooble')

    project.SaveToConfigParser(parser, 'greeble')
    flagsproj.SaveToConfigParser(parser, 'grooble')

    self.checkProject(
        launcher.Project.ProjectWithConfigParser(parser, 'greeble'),
        project.path, project.name, project.port)

    self.checkProject(
        launcher.Project.ProjectWithConfigParser(parser, 'grooble'),
        flagsproj.path, flagsproj.name, flagsproj.port, flags=flagsproj.flags)


if __name__ == '__main__':
  unittest.main()
