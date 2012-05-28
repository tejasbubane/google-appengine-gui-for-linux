#!/usr/bin/env python
#
# Copyright 2009 Google Inc.
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

"""Unittests for mainframe_selection_helper.py."""

import unittest
import launcher
from wxgladegen import main_frame


class FakeProject(object):
  """Mock class that stands in for a launcher.Project.

  The selection helper is just interested in the valid and runstate of
  projects, so this simple class lets tests create projects with exactly
  the desired settings, rather than trying to finesse launcher.Project into
  going into the correct state.
  """

  def __init__(self, valid, runstate):
    super(FakeProject, self).__init__()
    self._valid = valid
    self._runstate = runstate

  @property
  def valid(self):
    return self._valid

  @property
  def runstate(self):
    return self._runstate


class FakeMainFrame(object):
  """Mock class that stands in for a wx.MainFrame.

  The tests are interested in seeing what particular wx objects are enabled
  and disabled.  This fake MainFrame captures the operations that enabled
  and disable objects, and keeps track of what the final state will be.
  """

  def __init__(self):
    super(FakeMainFrame, self).__init__()
    self._disabled = set()
    self._enabled = set()

  def GetToolBar(self):
    """Tools are enabled/disabled via a toolbar."""
    return self

  def EnableTool(self, button_id, on_off):
    """This is a toolbar call to enable/disable a particular toolbar button."""
    self.Enable(button_id, on_off)

  def GetButtonByID(self, button_id):
    """This is a MainFrame call to map a button_id to a push button."""
    # Stash away the button id, since someone is going to be enable/disabling
    # it immediately.  This way we can tell in our Enable what button
    # should have its state changed.
    self._last_button_id = button_id
    return self

  def GetMenuBar(self):
    """Menu items are enabled/disabled via the menubar."""
    return self

  def Enable(self, arg1, arg2='not_passed'):
    """Bottleneck method for all enable/disable calls for objects.

    Args:
      arg1: For push buttons, this is the enabled/disabled flag
            For toolbar buttons and menus, this is their unique ID
      arg2: Not passed for push buttons
            For toolbar buttons and menus, this is the enabled/disabled flag.
    """
    if arg2 == 'not_passed':
      control_id = self._last_button_id
      enabled = arg1
    else:
      control_id = arg1
      enabled = arg2

    # Update our idea of what is enabled and disabled
    if control_id in self._disabled:
      self._disabled.remove(control_id)
    if control_id in self._enabled:
      self._enabled.remove(control_id)

    if enabled:
      self._enabled.add(control_id)
    else:
      self._disabled.add(control_id)

  @property
  def enabled_ids(self):
    return self._enabled

  @property
  def disabled_ids(self):
    return self._disabled


class MainFrameSelectionHelperTest(unittest.TestCase):
  """Exercise the MainFrameSelectionHelper class."""

  # All of the controls that can become enabled or disabled.
  ALL_CONTROL_IDS = frozenset((main_frame.APP_SETTINGS_MENU,
                               main_frame.BROWSE_MENU,
                               main_frame.DASHBOARD_BUTTON,
                               main_frame.DASHBOARD_MENU,
                               main_frame.DEPLOY_BUTTON,
                               main_frame.DEPLOY_MENU,
                               main_frame.EDIT_BUTTON,
                               main_frame.LOGS_BUTTON,
                               main_frame.LOGS_MENU,
                               main_frame.MINUS_BUTTON,
                               main_frame.OPEN_EXTERNAL_EDITOR_MENU,
                               main_frame.OPEN_FILE_BROWSER_MENU,
                               main_frame.REMOVE_PROJECT_MENU,
                               main_frame.RUN_BUTTON,
                               main_frame.RUN_MENU,
                               main_frame.RUN_STRICT_MENU,
                               main_frame.SDK_CONSOLE_BUTTON,
                               main_frame.SDK_CONSOLE_MENU,
                               main_frame.STOP_BUTTON,
                               main_frame.STOP_MENU,
                               main_frame.BROWSE_BUTTON))

  def setUp(self):
    self._main_frame = FakeMainFrame()
    self._helper = launcher.MainframeSelectionHelper()

  def _MakeProjects(self, enabled, state_list):
    """Build a list of fake projects.

    Args:
      enabled: A boolean whether the fake projects in the list should say they
               are valid (True) or invalid (False)
      state_list: list of launche.Project.STATE_*.

    Returns:
      A list of FakeProjects of the given states.
    """
    projects = []
    for state in state_list:
      projects.append(FakeProject(enabled, state))
    return projects

  def testEmptySelection(self):
    self._helper.AdjustMainFrame(self._main_frame, [])
    # An empty selection should result in everything disabled.
    self.assertEqual(self.ALL_CONTROL_IDS, self._main_frame.disabled_ids)
    # And nothing enabled
    self.assertFalse(self._main_frame.enabled_ids)

  def testEverythingEnabled(self):
    projects = self._MakeProjects(True,
                                  (launcher.Project.STATE_STOP,
                                   launcher.Project.STATE_RUN,
                                   launcher.Project.STATE_PRODUCTION_RUN,
                                   launcher.Project.STATE_STARTING,
                                   launcher.Project.STATE_DIED))
    self._helper.AdjustMainFrame(self._main_frame, projects)
    # Everything should be enabled
    self.assertEqual(self.ALL_CONTROL_IDS, self._main_frame.enabled_ids)
    # Nothing else should be disabled
    self.assertFalse(self._main_frame.disabled_ids)

  def testAllInvalid(self):
    projects = self._MakeProjects(False,
                                  (launcher.Project.STATE_STOP,
                                   launcher.Project.STATE_RUN,
                                   launcher.Project.STATE_PRODUCTION_RUN,
                                   launcher.Project.STATE_STARTING,
                                   launcher.Project.STATE_DIED))
    self._helper.AdjustMainFrame(self._main_frame, projects)
    # With everything invalid, we should still be able to remove projects.
    enabled_ids = set((main_frame.MINUS_BUTTON, main_frame.REMOVE_PROJECT_MENU))
    disabled_ids = self.ALL_CONTROL_IDS - enabled_ids
    self.assertEqual(enabled_ids, self._main_frame.enabled_ids)
    # Make sure everything else is disabled
    self.assertEqual(disabled_ids, self._main_frame.disabled_ids)

  def testRunStates(self):
    # All "runs" should have a disabled run button and menu.
    projects = self._MakeProjects(True,
                                  (launcher.Project.STATE_RUN,
                                   launcher.Project.STATE_RUN,
                                   launcher.Project.STATE_RUN))
    self._helper.AdjustMainFrame(self._main_frame, projects)
    disabled_ids = set((main_frame.RUN_BUTTON, main_frame.RUN_MENU,))
    enabled_ids = self.ALL_CONTROL_IDS - disabled_ids
    self.assertEqual(enabled_ids, self._main_frame.enabled_ids)
    self.assertEqual(disabled_ids, self._main_frame.disabled_ids)
    # All "production runs" should have disabled strict menu.
    projects = self._MakeProjects(True,
                                  (launcher.Project.STATE_PRODUCTION_RUN,
                                   launcher.Project.STATE_PRODUCTION_RUN))
    self._helper.AdjustMainFrame(self._main_frame, projects)
    disabled_ids = set((main_frame.RUN_STRICT_MENU,))
    enabled_ids = self.ALL_CONTROL_IDS - disabled_ids
    self.assertEqual(enabled_ids, self._main_frame.enabled_ids)
    self.assertEqual(disabled_ids, self._main_frame.disabled_ids)
    # A mix of production and regular runs should have everything enabled.
    projects = self._MakeProjects(True,
                                  (launcher.Project.STATE_PRODUCTION_RUN,
                                   launcher.Project.STATE_RUN,
                                   launcher.Project.STATE_PRODUCTION_RUN,
                                   launcher.Project.STATE_RUN))
    self._helper.AdjustMainFrame(self._main_frame, projects)
    self.assertFalse(self._main_frame.disabled_ids)
    self.assertEqual(self.ALL_CONTROL_IDS, self._main_frame.enabled_ids)

  def testBrowse(self):
    # Browse should only be enable if something is running
    projects = self._MakeProjects(True,
                                  (launcher.Project.STATE_STOP,
                                   launcher.Project.STATE_STARTING))
    self._helper.AdjustMainFrame(self._main_frame, projects)
    self.assertTrue(main_frame.BROWSE_MENU in self._main_frame.disabled_ids)
    self.assertFalse(main_frame.BROWSE_MENU in self._main_frame.enabled_ids)
    # Something in a runnable state should enable it.
    projects = self._MakeProjects(True,
                                  (launcher.Project.STATE_STOP,
                                   launcher.Project.STATE_STARTING,
                                   launcher.Project.STATE_DIED,
                                   launcher.Project.STATE_RUN))
    self._helper.AdjustMainFrame(self._main_frame, projects)
    self.assertFalse(main_frame.BROWSE_MENU in self._main_frame.disabled_ids)
    self.assertTrue(main_frame.BROWSE_MENU in self._main_frame.enabled_ids)
    # Something in a production run state should enable it.
    projects = self._MakeProjects(True,
                                  (launcher.Project.STATE_STOP,
                                   launcher.Project.STATE_STARTING,
                                   launcher.Project.STATE_DIED,
                                   launcher.Project.STATE_PRODUCTION_RUN))
    self._helper.AdjustMainFrame(self._main_frame, projects)
    self.assertFalse(main_frame.BROWSE_MENU in self._main_frame.disabled_ids)
    self.assertTrue(main_frame.BROWSE_MENU in self._main_frame.enabled_ids)
    # And both as well.
    projects = self._MakeProjects(True,
                                  (launcher.Project.STATE_RUN,
                                   launcher.Project.STATE_STOP,
                                   launcher.Project.STATE_STARTING,
                                   launcher.Project.STATE_DIED,
                                   launcher.Project.STATE_PRODUCTION_RUN))
    self._helper.AdjustMainFrame(self._main_frame, projects)
    self.assertFalse(main_frame.BROWSE_MENU in self._main_frame.disabled_ids)
    self.assertTrue(main_frame.BROWSE_MENU in self._main_frame.enabled_ids)

  def testStop(self):
    # Stop should be enabled if anything is running or starting
    projects = self._MakeProjects(True,
                                  (launcher.Project.STATE_STOP, ))
    self._helper.AdjustMainFrame(self._main_frame, projects)
    self.assertTrue(main_frame.STOP_MENU in self._main_frame.disabled_ids)
    self.assertTrue(main_frame.STOP_BUTTON in self._main_frame.disabled_ids)
    # Test run state.
    projects = self._MakeProjects(True,
                                  (launcher.Project.STATE_STOP,
                                   launcher.Project.STATE_DIED,
                                   launcher.Project.STATE_RUN))
    self._helper.AdjustMainFrame(self._main_frame, projects)
    self.assertTrue(main_frame.STOP_MENU in self._main_frame.enabled_ids)
    self.assertTrue(main_frame.STOP_BUTTON in self._main_frame.enabled_ids)
    # Test strict run state.
    projects = self._MakeProjects(True,
                                  (launcher.Project.STATE_STOP,
                                   launcher.Project.STATE_DIED,
                                   launcher.Project.STATE_PRODUCTION_RUN))
    self._helper.AdjustMainFrame(self._main_frame, projects)
    self.assertTrue(main_frame.STOP_MENU in self._main_frame.enabled_ids)
    self.assertTrue(main_frame.STOP_BUTTON in self._main_frame.enabled_ids)
    # Test strict starting state.
    projects = self._MakeProjects(True,
                                  (launcher.Project.STATE_STOP,
                                   launcher.Project.STATE_DIED,
                                   launcher.Project.STATE_STARTING))
    self._helper.AdjustMainFrame(self._main_frame, projects)
    self.assertTrue(main_frame.STOP_MENU in self._main_frame.enabled_ids)
    self.assertTrue(main_frame.STOP_BUTTON in self._main_frame.enabled_ids)
    # Kitchen-sink
    projects = self._MakeProjects(True,
                                  (launcher.Project.STATE_STOP,
                                   launcher.Project.STATE_RUN,
                                   launcher.Project.STATE_PRODUCTION_RUN,
                                   launcher.Project.STATE_STARTING))


if __name__ == '__main__':
  unittest.main()
