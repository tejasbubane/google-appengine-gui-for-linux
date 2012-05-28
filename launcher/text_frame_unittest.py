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
"""Unittests for text_frame.py"""

import unittest
import wx
import launcher


class TextFrameTest(unittest.TestCase):

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()

  def CreateConsole(self):
    """Create and return a generic console."""
    lc = launcher.TextFrame('title')
    return lc

  def testBasicTile(self):
    """Test to make sure new windows don't overlap."""
    pos = (0,0)
    launcher.TextFrame._ResetTiling()
    for i in range(3):
      lc = launcher.TextFrame('big bad window title')
      newpos = lc.GetPositionTuple()
      self.assertTrue(newpos[0] > pos[0])
      self.assertTrue(newpos[1] > pos[1])
      pos = newpos

  def testMuchTiling(self):
    """Make sure the top/left of our tile is always on-screen."""
    launcher.TextFrame._ResetTiling()
    area = wx.Display().GetClientArea()
    lc = launcher.TextFrame('super dooper tytle 4 roolerz and doodz')
    # Needs to be real big in case you have a large monitor.  ~1000
    # iterations needed for a (1440,874) laptop before a full reset
    # happens.
    for i in range(3000):
      lc._ShiftTilePosition()
      self.assertTrue(launcher.TextFrame._tile_position[0] > area[0])
      self.assertTrue(launcher.TextFrame._tile_position[1] > area[1])
      self.assertTrue(launcher.TextFrame._tile_position[0] < area[2])
      self.assertTrue(launcher.TextFrame._tile_position[1] < area[3])

  def testText(self):
    """Test adding text to the console."""
    lc = self.CreateConsole()
    contents = ""
    self.assertEqual(contents, lc.GetText())
    for str in ('a', 'foo', '\n\n\n', 'bar\nbaz\n choke choke zapf'):
      contents += str
      lc.AppendText(str)
      self.assertEqual(contents, lc.GetText())


if __name__ == '__main__':
  unittest.main()
