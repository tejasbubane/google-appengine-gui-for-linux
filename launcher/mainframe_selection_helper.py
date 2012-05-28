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


import launcher
from wxgladegen import main_frame


class MainframeSelectionHelper(object):
  """Helper class that adjusts the launcher's UI based on the selection"""

  def _EnableToolBarButtons(self, button_ids, enable):
    """Enable/Disable the toolbar buttons with the given IDs.

    Args:
      button_ids: list of toolbar button IDs to enable or disable
      enable: boolean value. True for enable a button, False to disable
    """
    toolbar = self._mainframe.GetToolBar()
    for button_id in button_ids:
      toolbar.EnableTool(button_id, enable)

  def _EnableButtons(self, button_ids, enable):
    """Enable/Disable the pushbuttons with the given IDs.

    Args:
      button_ids: list of pushbutton IDs to enable or disable
      enable: boolean value. True for enable a button, False to disable
    """
    for button_id in button_ids:
      button = self._mainframe.GetButtonByID(button_id)
      button.Enable(enable)

  def _EnableMenus(self, menu_item_ids, enable):
    """Enable/Disable the menu items with the given IDs.

    Args:
      menu_item_ids: list of menu item IDs to enable or disable
      enable: boolean value. True for enable a button, False to disable
    """
    menubar = self._mainframe.GetMenuBar()
    for menu_item_id in menu_item_ids:
      menubar.Enable(menu_item_id, enable)

  def _DisableEverything(self):
    """Disable all the controls that make sense to disable."""
    self._EnableToolBarButtons((main_frame.BROWSE_BUTTON,
                                main_frame.DASHBOARD_BUTTON,
                                main_frame.DEPLOY_BUTTON,
                                main_frame.EDIT_BUTTON,
                                main_frame.LOGS_BUTTON,
                                main_frame.RUN_BUTTON,
                                main_frame.SDK_CONSOLE_BUTTON,
                                main_frame.STOP_BUTTON), False)
    self._EnableButtons((main_frame.MINUS_BUTTON,), False)
    self._EnableMenus((main_frame.APP_SETTINGS_MENU,
                       main_frame.BROWSE_MENU,
                       main_frame.DASHBOARD_MENU,
                       main_frame.DEPLOY_MENU,
                       main_frame.LOGS_MENU,
                       main_frame.OPEN_EXTERNAL_EDITOR_MENU,
                       main_frame.OPEN_FILE_BROWSER_MENU,
                       main_frame.REMOVE_PROJECT_MENU,
                       main_frame.RUN_MENU,
                       main_frame.RUN_STRICT_MENU,
                       main_frame.SDK_CONSOLE_MENU,
                       main_frame.STOP_MENU), False)

  def _AnyProjectInState(self, selection, state):
    """Are any of the projects currently in the given runstate?"""
    projects = [p for p in selection if p.runstate == state]
    if projects:
      return True
    else:
      return False

  def _AnyProjectNotInState(self, selection, state):
    """Are any of the projects current not in the given runstate?"""
    projects = [p for p in selection if p.runstate != state]
    if projects:
      return True
    else:
      return False

  def _AllInvalidProjects(self, selection):
    """Are all of the projects invalid?"""
    projects = [p for p in selection if not p.valid]
    if projects == selection:
      return True
    else:
      return False

  def AdjustMainFrame(self, mainframe, selection):
    """Enable/Disable buttons, toolbar items, and menus based on the selection.

    These are the different commands, and their criteria for being enabled:
      * Run - anything selected and in stop state. Disable if all
              invalid or all running
      * Run Strict - anything selected and in stop state.  Disable if
                     all invalid.
      * Stop - anything selected in run, prod_run, starting state
      * Browse - anything selected and in run, prod_run
      * SDK Console - anything selected and in run, prod_run
      * Deploy - anything selected.  Disable if all invalid
      * Dashboard - anything selected.  Disable if all invalid
      * App Settings - anything selected.  Disable if all invalid
      * Open external editor - anything selected. Disable if all invalid
      * Open file browser - anything selected.  Disable if all invalid
      * Remove project - anything selected

    Args:
      mainframe: The top-level container object that holds the items to enable
                 or disable.
      selection: A list of launcher.Projects.  The run state and valid state
                 of the projects controls what gets enabled and disabled.
    """
    self._mainframe = mainframe

    # Turn everything off, then turn on the things that should be enabled.
    self._DisableEverything()
    if not selection:
      return

    # Always enabled if anything is selected.
    self._EnableButtons((main_frame.MINUS_BUTTON,), True)
    self._EnableMenus((main_frame.REMOVE_PROJECT_MENU,), True)

    # Everything else needs at least one valid project.
    if self._AllInvalidProjects(selection):
      return

    # Now juggle stuff based on run state.
    any_not_running = self._AnyProjectNotInState(selection,
                                                 launcher.Project.STATE_RUN)
    # Factor out constant to stay < 80 cols.
    prod_run_state = launcher.Project.STATE_PRODUCTION_RUN
    died_state = launcher.Project.STATE_DIED
    any_not_prod = self._AnyProjectNotInState(selection, prod_run_state)
    any_running = (self._AnyProjectInState(selection,
                                           launcher.Project.STATE_RUN) or
                   self._AnyProjectInState(selection, prod_run_state) or
                   self._AnyProjectInState(selection, died_state))
    any_starting = self._AnyProjectInState(selection,
                                           launcher.Project.STATE_STARTING)

    # These are independent of the projects' run state.
    self._EnableToolBarButtons((main_frame.EDIT_BUTTON,
                                main_frame.DEPLOY_BUTTON,
                                main_frame.DASHBOARD_BUTTON,
                                main_frame.LOGS_BUTTON), True)
    self._EnableMenus((main_frame.APP_SETTINGS_MENU,
                       main_frame.OPEN_EXTERNAL_EDITOR_MENU,
                       main_frame.OPEN_FILE_BROWSER_MENU,
                       main_frame.DEPLOY_MENU,
                       main_frame.DASHBOARD_MENU,
                       main_frame.LOGS_MENU), True)

    # Can only run if there are stopped projects.
    self._EnableToolBarButtons((main_frame.RUN_BUTTON,),
                               any_not_running)

    self._EnableMenus((main_frame.RUN_MENU,), any_not_running)
    self._EnableMenus((main_frame.RUN_STRICT_MENU,), any_not_prod)

    # Can only stop running (or starting) projects.
    self._EnableToolBarButtons((main_frame.STOP_BUTTON,),
                               any_running or any_starting)
    self._EnableMenus((main_frame.STOP_MENU,), any_running or any_starting)

    # Can only browse running projects.
    self._EnableToolBarButtons((main_frame.BROWSE_BUTTON,
                                main_frame.SDK_CONSOLE_BUTTON), any_running)
    self._EnableMenus((main_frame.BROWSE_MENU,
                       main_frame.SDK_CONSOLE_MENU), any_running)
