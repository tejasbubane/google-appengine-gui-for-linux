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

"""Unittests for mainframe.py"""

import shutil
import tempfile
import unittest
import wx
import launcher

class MainFrameTest(unittest.TestCase):
  """Exercise the MainFrame class"""

  class FakeTable(object):
    def ProjectAtIndex(self, index):
      return index

  class FakeListCtrl(launcher.ResizingListCtrl):
    """Simulate some ListCtrl selection functions for selection testing."""
    def __init__(self, parent):
      super(MainFrameTest.FakeListCtrl, self).__init__(parent, -1,
                                                       style=wx.LC_REPORT)
      self._selection = []
      self._itemCount = 0
      self.valid = 0
      self.invalid = 0

    def SetItemCount(self, count):
      self._itemCount = count

    def GetItemCount(self):
      return self._itemCount

    def IsSelected(self, index):
      return index in self._selection

    def Select(self, index, on=1):
      if on:
        self._selection.append(index)
      elif index in self._selection:
        self._selection.remove(index)

    # This is not a listctrl cover method.
    def UnselectAll(self):
      self._selection = []

    def _MarkRowValidity(self, listCtrl, row, valid):
      if valid:
        self.valid += 1
      else:
        self.invalid += 1

  class ClipboardMainFrame(launcher.MainFrame):
    """A MainFrame subclass  that lets you fake the contents of the clipbard."""

    def SetClipboardText(self, text):
      """'Copy' something to the 'clipboard'."""
      self._text = text

    def _GetTextFromClipboard(self):
      """Retrieve the contents of the 'clipboard'."""
      return self._text

  class FakeAppController(object):
    """A fake app controller that see the path being passed to Add()."""

    def __init__(self):
      self._path = None

    def Add(self, event, path):
      self._path = path

    def SetPath(self, path):
      self._path = path

    def GetPath(self):
      return self._path

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()
    ac = launcher.AppController(self.app)
    self.frame = launcher.MainFrame(None, -1, launcher.MainTable(), None, ac,
                                    None)

    # Make the fake table and list control for selecton tests.
    fake_table = MainFrameTest.FakeTable()
    fake_listctrl = MainFrameTest.FakeListCtrl(wx.Frame(None, -1))
    self.frame._table = fake_table
    self.frame._listctrl = fake_listctrl

  def tearDown(self):
    self.frame = None

  def testSelectedProjects(self):
    """Test selection processing algorithm

    Tests the selection processing algorithm by providing the MainFrame a
    fake table (which returns "projects" at a given index) and a
    fake list control (which returns a discontiguous set of "selections")
    """

    self.frame._listctrl.SetItemCount(5)
    self.frame._listctrl.Select(0)
    self.frame._listctrl.Select(1)
    self.frame._listctrl.Select(2)
    self.frame._listctrl.Select(4)

    projects = self.frame.SelectedProjects()

    self.assertEqual(4, len(projects))
    self.assertEqual(0, projects[0])
    self.assertEqual(1, projects[1])
    self.assertEqual(2, projects[2])
    self.assertEqual(4, projects[3])

  def testRestoredSelection(self):
    """Test setting of the selection."""
    self.frame._listctrl.SetItemCount(10)
    # Select the ends of the range, a continuous range, and a solo outlier.
    self.frame._listctrl.Select(0)
    self.frame._listctrl.Select(2)
    self.frame._listctrl.Select(3)
    self.frame._listctrl.Select(4)
    self.frame._listctrl.Select(5)
    self.frame._listctrl.Select(9)

    projects = self.frame.SelectedProjects()

    self.frame._listctrl.UnselectAll()
    # Sanity-check the test class.
    shouldBeNoProjects = self.frame.SelectedProjects()
    self.assertEqual(0, len(shouldBeNoProjects))

    # Restore the selection
    self.frame.SetSelectedProjects(projects)

    # Make sure we what got what we wanted restored.
    projects2 = self.frame.SelectedProjects()
    self.assertEqual(6, len(projects2))
    self.assertEqual(projects, projects2)

  def testUnselectAll(self):
    """Test unselecting everything"""
    self.frame._listctrl.SetItemCount(10)

    self.frame._listctrl.Select(1)
    self.frame._listctrl.Select(3)
    self.frame._listctrl.Select(5)

    # Sanity-check initial conditions
    projects = self.frame.SelectedProjects()
    self.assertEqual(3, len(projects))

    self.frame.UnselectAll()
    projects = self.frame.SelectedProjects()
    self.assertEqual(0, len(projects))

  def testWindowPositionSaving(self):
    file = tempfile.NamedTemporaryFile()
    prefs = launcher.Preferences(file.name)

    mainframe = launcher.MainFrame(None, -1, launcher.MainTable(), prefs,
                                   None, None)
    mainframe.SetPosition((10, 20))
    mainframe.SetSize((500, 600))
    mainframe.Close()

    # Make sure the size gets saved... but adjusted for minimum sizing.
    rect = prefs.Get(launcher.Preferences.PREF_MAIN_WINDOW_RECT)
    self.assertEqual('10 20 500 600', rect)

    # Make sure the size gets restored... but adjusted for minimum sizing.
    mainframe = launcher.MainFrame(None, -1, launcher.MainTable(), prefs,
                                   None, None)
    position = mainframe.GetPositionTuple()
    self.assertEqual((10, 20), position)
    size = mainframe.GetSizeTuple()
    self.assertEqual((500, 600), size)

    # Make sure an off-the-screen window gets moved elsewhere
    prefs.Set(launcher.Preferences.PREF_MAIN_WINDOW_RECT, '-300 -900 300 400')
    mainframe = launcher.MainFrame(None, -1, launcher.MainTable(), prefs,
                                   None, None)
    position = mainframe.GetPositionTuple()
    self.assertNotEqual((-300, -900), position)
    size = mainframe.GetSizeTuple()
    self.assertEqual((300, 400), size)

    # Clean up our temp prefs file.
    file.close()

  def testWindowMinSize(self):
    file = tempfile.NamedTemporaryFile()
    prefs = launcher.Preferences(file.name)

    mainframe = launcher.MainFrame(None, -1, launcher.MainTable(), prefs,
                                   None, None)
    mainframe.SetPosition((10, 20))
    mainframe.SetSize((100, 50))
    size = mainframe.GetSizeTuple()
    self.assertEqual(launcher.MainFrame.WINDOW_MIN_SIZE, size)

    file.close()

  def testInvalidProject(self):
    projects = []
    for valid in (False, True, False):
      p = launcher.Project('/tmp/foo', 8000)
      p._valid = valid
      projects.append(p)
    self.frame._MarkRowValidity = self.frame._listctrl._MarkRowValidity
    self.frame.RefreshView(projects)
    self.assertEqual(1, self.frame._listctrl.valid)
    self.assertEqual(2, self.frame._listctrl.invalid)

  def testBuildDemoMenu(self):
    demodir = tempfile.mkdtemp()
    demos = ['hi', 'mom', 'sooper-dooper-demo']
    for name in demos:
      os.mkdir(os.path.join(demodir, name))
    pong_demos = []
    def CreateDemoByNameFunction(path):
      pong_demos.append(os.path.basename(path))
    self.frame._CreateDemoByNameFunction = CreateDemoByNameFunction
    self.frame._BuildDemoMenu(demo_dir=demodir)
    self.assertEqual(demos, pong_demos)
    shutil.rmtree(demodir)

  def testDemoByNameFunction(self):
    f = self.frame._CreateDemoByNameFunction('path')
    self.assertTrue(callable(f))

  def testPaste(self):
    ac = self.FakeAppController()
    self.frame = self.ClipboardMainFrame(None, -1, launcher.MainTable(),
                                         None, ac, None)
    # Pretend to paste a valid path.  This path should get to the fake
    # app controller.
    platform = launcher.Platform()
    self.frame.SetClipboardText(platform.AppEngineBaseDirectory())
    self.frame.OnPaste(None)
    self.assertEqual(platform.AppEngineBaseDirectory(), ac.GetPath())
    # Pretend to paste an invalid path.  The path should not find its way
    # to the fake app controller.
    self.frame.SetClipboardText('unga wunga bunga')
    ac.SetPath(None)
    self.frame.OnPaste(None)
    self.assertFalse(ac.GetPath())

if __name__ == '__main__':
  unittest.main()
