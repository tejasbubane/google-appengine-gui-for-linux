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
"""Controller (MVC) for our About Box.  The about box is an
HtmlInfoDialog defined in html_info_dialog.py.
"""

import logging
import os
import sys
import webbrowser
import wx
import wx.html
import launcher


class AboutBoxException(Exception):
  """Exceptional condition for About Box use, such as html content not found."""
  pass


class AboutBoxController(object):
  """Controller (MVC) for our About Box."""

  _CONTENT_FILENAME = 'html/about_box.html'

  _TITLE = 'About Google App Engine Launcher'
  _SIZE = (450, 480)

  def __init__(self):
    super(AboutBoxController, self).__init__()
    self._dialog = None
    self._preferences = launcher.Preferences()
    self._CreateDialog()
    self._CreateHtmlContent()
    self._SetPage()

  def __del__(self):
    """Honor wx Dialog memory semantics."""
    if self._dialog:
      self._dialog.Destroy()

  def _CreateDialog(self):
    self._dialog = launcher.HtmlInfoDialog(None, -1,
                                           title=self._TITLE,
                                           size=self._SIZE)
    # We'll need this later...
    self._background_color = self._dialog.GetBackgroundColour()

    # Attach some behaviors
    self._dialog.BindOK(self._OnEndModalOK)
    self._dialog.BindLink(self._OnLinkClicked)

  def _CreateHtmlContent(self):
    """Create content for this About Dialog."""
    try:
      self._content_string = open(self._CONTENT_FILENAME).read()
    except IOError:
      raise AboutBoxException('Cannot open or read about box content')

    # Grab SDK version information
    sdk_version = '???'  # default
    sdk_dir = self._preferences[launcher.Preferences.PREF_APPENGINE]
    if sdk_dir:
      sdk_version_file = os.path.join(sdk_dir, 'VERSION')
      try:
        sdk_version = '<br>'.join(open(sdk_version_file).readlines())
      except IOError:
        pass

    # By default, wx.html windows have a white background.  We'd
    # prefer a standard window background color.  Although there is
    # a wx.html.HtmlWindow.SetBackgroundColour() method, it doesn't
    # help us.  The best we can do is set the background from within
    # the html itself.
    bgcolor = '#%02x%02x%02x' % self._background_color[0:3]

    # Replace some strings with dynamically determined information.
    text = self._content_string
    text = text.replace('{background-color}', bgcolor)
    text = text.replace('{launcher-version}', '???')  # TODO(jrg): add a version
    text = text.replace('{python-version}', sys.version.split()[0])
    text = text.replace('{wxpython-version}', wx.version())
    text = text.replace('{sdk-version}', sdk_version)
    self._content_string = text

  def _SetPage(self):
    """Set the html content page of our dialog."""
    self._dialog.SetPage(self._content_string)

  def _OnEndModalOK(self, evt):
    """Called by a button (OK) which ends the modal session."""
    self._dialog.EndModal(wx.ID_OK)

  def _OnLinkClicked(self, evt, browsefunc=webbrowser.open):
    """Called by our html window when a link is clicked.

    Args:
      evt: an event (standard call convention for wx event handler)
      browsefunc: the function we use to browse the link which
        returns True if we could browse successfully.
    """
    linkinfo = evt.GetLinkInfo()
    link = linkinfo.GetHref()
    worked = browsefunc(link)
    if not worked:
      logging.warning('Could not open link %s' % link)

  def ShowModal(self):
    """Run modally."""
    return self._dialog.ShowModal()
