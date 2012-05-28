#!/usr/bin/env python
#
# Copyright 2008 Google Inc.  All Rights Reserved.
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

"""Base Controller (MVC) for project-related dialogs controllers.

The base class handles a few common operations, like binding OK/Cancel
and destroying the dialog properly when done.
"""


import wx


class DialogControllerBase(object):
  """Base class for controllers for project dialogs."""

  def __init__(self):
    super(DialogControllerBase, self).__init__()
    self.dialog = None

  def __del__(self):
    """Honor wx Dialog memory semantics."""
    if self.dialog:
      self.dialog.Destroy()

  def FailureMessage(self, message, caption):
    """Display a warning to the user about a non-fatal failure.

    Split into a separate method for easier unit testing.
    Args:
      message: the message to display.
      caption: a caption for the dialog.
    """
    wx.MessageBox(message, caption, style=wx.OK|wx.ICON_ERROR)

  def EndModalClosure(self, dialog, code):
    """Create an event callback for ending a modal dialog.

    Args:
      dialog: the dialog to call EndModal() on
      code: the arg to EndModal() that will be used
    Returns:
      A closure suitable for passing as a handler to wx.Frame.Bind()
    """
    def EndModal(evt):
      dialog.EndModal(code)
    return EndModal

  def MakeBindingsOKCancel(self):
    """Bind events on our dialog.

    In the base class we only bind the Update (OK) and Cancel buttons.
    We define wx.ID_OK as the return of an 'Update'.  self.dialog must
    have OK/Update and Cancel buttons.
    """
    dialog = self.dialog
    if hasattr(dialog, 'update_button'):
      ok_or_update_button = dialog.update_button
    else:
      ok_or_update_button = dialog.ok_button
    dialog.Bind(wx.EVT_BUTTON, self.EndModalClosure(dialog, wx.ID_OK),
                ok_or_update_button)
    dialog.Bind(wx.EVT_BUTTON, self.EndModalClosure(dialog, wx.ID_CANCEL),
                dialog.cancel_button)
