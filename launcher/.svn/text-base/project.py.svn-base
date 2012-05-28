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

import logging
import os
import sys
import ConfigParser

class ProjectException(Exception):
  """Exceptional project condition, such as bad arguments to __init__."""

class Project(object):
  """Basic definition of an app engine project ('application')."""

  # Run states for a project
  STATE_STOP = 0
  STATE_RUN = 1
  STATE_PRODUCTION_RUN = 2
  STATE_STARTING = 3
  STATE_DIED = 4

  # All the states in one ready to eat package.
  ALL_STATES = (STATE_STOP, STATE_RUN, STATE_PRODUCTION_RUN,
                STATE_STARTING, STATE_DIED)

  @staticmethod
  def ProjectWithConfigParser(configParser, sectionName):
    """Create a project from a config file.

    Args:
      configParser: A ConfigParser that contains a section which has the values
          for creating a new Project (path, port, and name).
      sectionName: The section name under which to look for the Project's
          attributes.
      Both configParser and sectionName need to be non-empty values

    Returns:
      A newly created and populated Project.

    Raises:
      ProjectException if there are bad arguments or there was trouble
      reading the project's attributes from the configuration section.
    """

    if not configParser or sectionName is None:
      raise ProjectException('configParser and sectionName are required '
                             'to be non-zero values')

    pathport = Project._LoadFromConfigParser(configParser, sectionName)

    return Project(pathport[0], pathport[1], name=pathport[2],
                   flags=pathport[3])


  def __init__(self, path, port, name=None, flags=None):
    """Create a new project.

    Args:
      path: filesystem path of the project.
      port: The project's port.  This should be a numeric value, or a value
            that can be converted to a numeric value.
      name: A short name for the project.
      flags: A tuple of project flags.

    Raises:
      ProjectException if the argments are bad (None/zero values for path and
      port), or if the path, port, or name have leading or trailing spaces,
      since those will cause ConfigParser to write a file that it can't
      re-parse.
    """
    if not path or not port:
      raise ProjectException('Path and port are required to be non-zero values')

    # self._runstate: our run state (STATE_RUN, STATE_STOP, etc)
    # self._path: the filesystem path of the project
    # self._name: a short name for this project
    # self._port: the local port we'll use when running our application
    # self._flags: list of extra command line flags for this project
    self._runstate = self.STATE_STOP

    self._path = path.strip()
    self._port = int(port)

    name_from_yaml = self._GetProjectNameFromYamlFile()
    self._name = name or name_from_yaml or os.path.basename(path)
    self._name = self._name.strip()

    # TODO(jrg): prevent changing of flags while running?
    # Perhaps just disallow GetInfo dialog while running.
    self.flags = flags  # calls a function to verify

    # self.valid: True if valid (exists on disk etc)
    # Set by Verify()
    self._valid = False
    self.Verify()

  def __eq__(self, other):
    """Clearly define equality for projects (filesystem uniqueness)."""
    # TODO(jrg): os.path.samefile?  What is the Win equivalent?
    return self._path == other._path and self._port == other._port

  def __ne__(self, other):
    """Clearly define inequality for projects."""
    return not self.__eq__(other)

  @property
  def name(self):
    """A project's name is read-only."""
    return self._name

  @property
  def path(self):
    """A project's path is read-only."""
    return self._path

  def _GetPort(self):
    """Getter for a project's port."""
    return self._port

  def _SetPort(self, port):
    """Set the port of a project; it cannot be while the project is running.

    Args:
      port: the port we wish to use
    Raises:
      ProjectException: raised if the project is already running
    """
    if self._runstate == self.STATE_STOP:
      self._port = int(port)
    else:
      raise ProjectException('Attempt to set port of a running project')

  port = property(_GetPort, _SetPort,
                  doc='Get or set the port of a project.')

  def _GetRunState(self):
    return self._runstate

  def _SetRunState(self, state):
    if state in self.ALL_STATES:
      self._runstate = state
    else:
      raise ProjectException('Attempt to set runstate to bogus value')

  runstate = property(_GetRunState, _SetRunState,
                      doc='Get or set the runstate of a project')

  def _GetFlags(self):
    return self._flags

  def _SetFlags(self, flags):
    flags = flags or []
    if not getattr(flags, '__iter__', False):
      raise ProjectException('flags must be a tuple, or None')
    self._flags = flags
    pass

  flags = property(_GetFlags, _SetFlags, doc='Get or set tuple of flags')

  @property
  def valid(self):
    """A project's valid state is read-only."""
    return self._valid

  # TODO(jrg): use the yaml library for parsing app.yaml.  I cheat
  # for now to avoid worrying about how to package it
  def _GetProjectNameFromYamlFile(self):
    """Return the project name from our app.yaml file.

    Returns:  Our project name, or None.
    """
    name = None
    app_yaml = os.path.join(self._path, 'app.yaml')
    try:
      lines = open(app_yaml, 'r').readlines()
      for line in lines:
        words = line.split()
        if (len(words) >= 2) and words[0] == 'application:':
          name = words[1].strip()
          break
    except IOError:
      # Doesn't exist, can't open for read, ...
      pass
    return name

  def Verify(self):
    """Verify if a project is valid.

    Set its self._valid state (e.g. False if not on disk).
    Also updates self.name if changed out from under us.
    """
    self._valid = True
    name = self._GetProjectNameFromYamlFile()
    if not name:
      self._valid = False
    else:
      # Pick up a new name if needed.
      if name != self._name:
        self._name = name

  def SaveToConfigParser(self, parser, sectionName):
    """Write the project's attributes to the ConfigParser.

    Args:
      parser: A ConfigParser to save the Project to.
      sectionName: The section name under which to save the Project's
          attributes.
    """
    parser.set(sectionName, 'name', self.name)
    parser.set(sectionName, 'path', self.path)
    parser.set(sectionName, 'port', str(self.port))
    count = 0
    for flag in self._flags:
      name = 'flag%d' % count
      count += 1
      parser.set(sectionName, name, flag)

  @staticmethod
  def _LoadFromConfigParser(parser, sectionName):
    """Read the project's attributes from a ConfigParser.

    Args:
      configParser: A ConfigParser that contains a section which has the values
          for creating a new Project (path, port, and name)
      sectionName: The section name under which to look for the Project's
          attributes.

    Returns:
      A tuple with the read path, port, name, and flags, in that order.
      Flags is itself a tuple of strings.

    Raises:
      ProjectException if the name, path, and port could not be read from
      the ConfigParser.
    """
    name = parser.get(sectionName, 'name')
    path = parser.get(sectionName, 'path')
    port = int(parser.get(sectionName, 'port'))
    flags = []
    # Flag keys are named flag0, flag1, ...
    options = [o for o in parser.options(sectionName) if o.startswith('flag')]
    # Special cmp so flags10 comes AFTER flags9
    options.sort(cmp=lambda a, b: int(a.strip('flag')) - int(b.strip('flag')))

    # sorted() to keep stable
    for opt in sorted(options):
      flags.append(parser.get(sectionName, opt))

    # It's fine to have no flags; no need to check.
    return (path, port, name, flags)
