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
import wx.html
import launcher


class HtmlInfoDialog(wx.Dialog):
  """Informational dialog with an html display window and an OK button.

  The wx.Dialog's named arg size (for its __init__) can be used to
  set the dialog size.  If the html content doesn't fit in it the
  specified area, a scrollbar is added.
  """
  # Implementation note: I started with this dialog using wxGlade, but
  # it's just too simple (2 items!) for wxGlade to make things easier.
  def __init__(self, *args, **kwds):
    super(launcher.HtmlInfoDialog, self).__init__(*args, **kwds)
    self._CreateContent()

  def _CreateContent(self):
    """Create content for this dialog (e.g. OK button)."""
    self._html_window = wx.html.HtmlWindow(self, -1)
    self._ok_button = wx.Button(parent=self, label='OK')
    self._ok_button.SetDefault()

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(self._html_window, proportion=1,
              flag=wx.FIXED_MINSIZE|wx.EXPAND, border=8)
    sizer.Add((16,16))
    sizer.Add(self._ok_button, proportion=0, border=16,
              flag=wx.FIXED_MINSIZE|wx.RIGHT|wx.BOTTOM|wx.ALIGN_RIGHT)
    self.SetSizer(sizer)
    self.Layout()
    self.FitInside()
    self.Centre()

  def BindOK(self, callback):
    """Bind a call to the OK button (click)."""
    self.Bind(wx.EVT_BUTTON, callback, self._ok_button)

  def BindLink(self, callback):
    """Bind a call to a link click in our html."""
    self.Bind(wx.html.EVT_HTML_LINK_CLICKED, callback, self._html_window)

  def SetPage(self, content_string):
    """Set content for the html window for this dialog.

    Although a better name might be SetHtmlContentString(), I'm trying
    to be consistent with the wx naming convention.

    Args:
      content_string: a string of html (not a filename)
    """
    self._html_window.SetPage(content_string)

  def ToText(self):
    """Returns page contents.  For unit testing."""
    return self._html_window.ToText()
