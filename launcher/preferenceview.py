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

import wx
import launcher


class PreferenceView(wx.Dialog):
  """View (V in MVC) for the preferences dialog.

  A PreferenceView is managed by PreController (C in MVC).
  It does not have a pointer to preference data (M in MVC).
  """

  # Constants used for object size/positioning
  _PREF_SHORT_TEXT_WIDTH = 1
  _PREF_BUTTON_WIDTH = 1
  _PREF_CONTROL_WIDTH = 20
  _PREF_DESCRIPTION_WIDTH = 20
  _PREF_DESCRIPTION_HEIGHT = 2

  def __init__(self):
    super(PreferenceView, self).__init__(None, -1, 'Preferences')
    # Note: no need for a wx.Panel in a wx.Dialog
    self._sizer = wx.GridBagSizer(vgap=5, hgap=5)
    self._x_index = 1    # indices for adding items to the dialog
    self._y_index = 1
    self._text_controls = {}  # wx.TextCtrls indexed by key (pref)
    self.selectors = {}  # selector type (file, directory) indexed by key (pref)
    self.SetSizer(self._sizer)

  # TODO(jrg): this is messy; fix.
  def Append(self, prefname,
             summary='',
             description='',
             file_selector=False,
             dir_selector=False,
             value=None,
             default=None):
    """Append a preference item to the dialog.

    Args:
      prefname: A dictionary key to reference this preference later
      summary: A very short description of the preference
      description: A longer descriptive text to display in the dialog
      file_selector: If True, display a button which provides a file selector
        to update the preference
      dir_selector: If True, display a button which provides a directory
        selector to update the preference
      value: current value for this preference.
      default: A default used by the launcher if the pref is NOT set.

    If both file_selector and dir_selector are set to True, behavior
    is undefined.
    """
    # TODO(jrg): this is prime for refactoring (e.g. an object for each pref
    # which has it's own containing sizer).  Do so after talking with skidgel
    # for UI feedback.  Ditto for _Position().
    short_text = wx.StaticText(self, -1, summary)
    control = wx.TextCtrl(self, -1)
    if value:
      control.ChangeValue(value)
    button = None
    if file_selector or dir_selector:
      button = wx.Button(parent=self, label='Select...')
      button.SetName(prefname)
      if file_selector:
        self.selectors[prefname] = 'file'
        self.Bind(wx.EVT_BUTTON, self._OnFileButton, button)
      else:
        self.selectors[prefname] = 'directory'
        self.Bind(wx.EVT_BUTTON, self._OnDirectoryButton, button)
    long_description = description
    if default:
      long_description += '\nDefault if not set: ' + default
    long_text = wx.StaticText(self, -1, long_description,
                            style=wx.TE_MULTILINE|wx.TE_READONLY)
    # Save it and position
    self._text_controls[prefname] = control
    self._Position(short_text, control, button, long_text)

  def PreferenceCount(self):
    """Return the number of preferences we will display"""
    return len(self._text_controls)

  def _Position(self, short_text, control, button, long_text):
    """Position the objects for a preference.

    Args:
      short_text: short text description wx.Window
      control: text entry wx.Window
      button: if not None, button to bring up file/dir dialog
      long_text: long description wx.Window
    Modifies current position indices (self._x_index etc)
    """
    x = self._x_index
    y = self._y_index

    # row1: text, control, (optional) button
    self._sizer.Add(short_text, pos=(y, x),
                    span=(1, self._PREF_SHORT_TEXT_WIDTH))
    x += self._PREF_SHORT_TEXT_WIDTH
    self._sizer.Add(control, pos=(y, x), span=(1, self._PREF_CONTROL_WIDTH),
                    flag=wx.EXPAND)
    x += self._PREF_CONTROL_WIDTH
    if button:
      self._sizer.Add(button, pos=(y, x), span=(1, self._PREF_BUTTON_WIDTH))
      x += self._PREF_BUTTON_WIDTH

    # row2-4: description
    y += 1
    x = 1 + self._PREF_SHORT_TEXT_WIDTH
    self._sizer.Add(long_text, pos=(y,x),
                    span=(self._PREF_DESCRIPTION_HEIGHT,
                          self._PREF_DESCRIPTION_WIDTH),
                    flag=wx.EXPAND)
    y += 1 + self._PREF_DESCRIPTION_HEIGHT

    # where we start next time
    self._y_index = y

  def _OnFileButton(self, evt):
    """Called when a File selector button was clicked."""
    d = wx.FileDialog(None, style=wx.FD_FILE_MUST_EXIST)
    self._OnFileDirectoryButtonCommon(evt, d)

  def _OnDirectoryButton(self, evt):
    """Called when a Directory selector button was clicked."""
    d = wx.DirDialog(None, style=wx.DD_DIR_MUST_EXIST)
    self._OnFileDirectoryButtonCommon(evt, d)

  def _NameFromEvent(self, evt):
    """Return the name of the object which generated this event, or None.

    Split out to make unit testing easier.
    """
    name = None
    button = self.FindWindowById(evt.GetId())
    if button:
      name = button.GetName()
    return name

  # Technically this mixes V and C, but it's such little logic I'm not ashamed.
  def _OnFileDirectoryButtonCommon(self, evt, dialog):
    """Commmon file/dialog selector button routine.

    Args:
      dialog: a wx.Dialog class for item selection
    """
    name = self._NameFromEvent(evt)
    if dialog.ShowModal() == wx.ID_OK:
      path = dialog.GetPath()
      self._text_controls[name].SetValue(path)

  def _OnEndModalOK(self, evt):
    """Called by a button (OK) which ends the modal session."""
    self.EndModal(wx.ID_OK)

  def _OnEndModalCancel(self, evt):
    """Called by a button (Cancel) which ends the modal session."""
    self.EndModal(wx.ID_CANCEL)

  def _FinishCreateDialog(self):
    """Finish creating the dialog.

    If called, we will not be adding any more items.
    Thus, it's safe to add OK/Cancel buttons at the bottom.
    """
    self._sizer.Fit(self)
    cols = self._sizer.GetCols()
    y = self._y_index
    y += 1
    ok = wx.Button(parent=self, label='OK')
    cancel = wx.Button(parent=self, label='Cancel')
    self._sizer.Add(cancel, pos=(y, cols-3))
    self._sizer.Add(ok, pos=(y, cols-1))
    y += 1
    self._sizer.Add((0, 0), pos=(y, cols))
    self.Bind(wx.EVT_BUTTON, self._OnEndModalOK, ok)
    self.Bind(wx.EVT_BUTTON, self._OnEndModalCancel, cancel)
    ok.SetDefault()
    self._sizer.Fit(self)

  def ShowModal(self):
    """Show the dialog modally.

    Override of wx.Dialog.ShowModal() to insure the
    dialog is completed before display.
    """
    self._FinishCreateDialog()
    return super(PreferenceView,self).ShowModal()

  def Get(self, pref):
    """Get the value for a preference.

    Args:
      pref: the dictionary key originally passed in with Append()
    Returns:
      the preference setting from the dialog, which may be None.
    """
    if pref not in self._text_controls:
      return None
    return self._text_controls[pref].GetValue()
