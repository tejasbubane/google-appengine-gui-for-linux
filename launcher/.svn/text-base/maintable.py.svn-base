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

import ConfigParser
import operator
import os
import sys
import wx
import launcher

class MainTable(object):
  """Our main model (MVC), consisting of our list of projects."""

  def __init__(self, filename=None):
    """Create a new MainTable."""

    # self._projects: an array of Projects in this table
    self._projects = []
    self._platform = launcher.Platform()
    self._filename = filename or self._platform.ProjectsFile()
    self._LoadProjects(self._filename)

  def UniquePort(self):
    """Return a port not otherwise used by existing projects."""
    if not self._projects:
      return 8080
    return max(self._projects, key=operator.attrgetter('port')).port + 1

  def SaveProjects(self):
    """Save all of the projects to the configuration file.

    The projects are saved to the path provided in __init__.
    Each project saves itself to a section of the ConfigParser, with the
    section name being the position in the list in the UI.

    A sample file can be found in testdata/project1.ini.
    """
    parser = ConfigParser.ConfigParser()

    i = 0
    for project in self._projects:
      name = str(i)
      parser.add_section(name)
      project.SaveToConfigParser(parser, name)
      i += 1

    try:
      fp = file(self._filename, 'w')
      fp.write('# Gogle App Engine Launcher Project File\n')
      fp.write('# http://code.google.com/appengine\n\n');
      parser.write(fp)
      fp.close()
    except IOError, err:
      (errno, strerror) = err
      self._MainTableProblem('Could not save into projects file %s: %s' %
                             (self._filename, strerror))

  def _LoadProjects(self, filename):
    """Read the projects from a file.

    This construct new Projects from the file's contents, and replace our
    _projects array with the new projects.
    """
    self._projects = []

    parser = ConfigParser.ConfigParser()
    parser.read(filename)

    sections = sorted(parser.sections(), key=lambda x: int(x))

    for sectionname in sections:
      project = launcher.Project.ProjectWithConfigParser(parser, sectionname)
      self._AddProject(project)

  def _AddProject(self, project):
    """Add a new project to our table, and ping the UI for an update.

    Args:
      project: the Project to add to the table.
    """
    self._projects.append(project)

  def AddProject(self, project):
    """Add a new project to the table, signal UI for an update, save to disk.

    Args:
      project: the Project to add to the table.
    """
    self._AddProject(project)
    self.SaveProjects()

  def RemoveProject(self, project):
    """Remove a project from our table, and ping the UI for an update.

    Args:
      project: the Project to remove from our table.
    """
    self._projects.remove(project)
    self.SaveProjects()

  def _MainTableProblem(self, str):
    """We had a problem saving or loading the project file; tell the user."""
    wx.MessageBox(str, 'Projects', style=wx.CENTRE|wx.OK|wx.ICON_ERROR)

  def ProjectAtIndex(self, index):
    """Return the project that lives at a given index."""
    try:
      return self._projects[index]
    except IndexError:
      return None

  def ProjectCount(self):
    """Return the number of projects"""
    return len(self._projects)

  def Verify(self):
    """Ask each project to verify itself (e.g. exists on disk)."""
    [p.Verify() for p in self._projects]
