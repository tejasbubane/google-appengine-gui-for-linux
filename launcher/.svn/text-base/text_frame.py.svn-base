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


class TextFrame(wx.Frame):
  """TextFrame is a generic output frame (view in MVC) for text.

  A typical use for a TextFrame is to display output of a running
  process.  The text frame class has a few convenience routines that
  maintain state across instances (e.g. initial tile position).
  """

  # Positional variables for tiling console windows.
  _tile_initial_reset = [200, 200]
  _tile_initial = _tile_initial_reset[:]
  _tile_position = _tile_initial[:]
  _TILE_SKIP = (32, 32)

  def __init__(self, title):
    """Create a new TextFrame.

    Args:
      title: The title for our window.
    """
    super(TextFrame, self).__init__(None, -1, title, size=(650,300))
    tc_styles = wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH
    self._text_ctrl = wx.TextCtrl(self, style=tc_styles)
    text_style = wx.TextAttr()
    # Oddly, 12pt works fine on Mac OS but seems to too big on Windows.
    # TODO(jrg): platform.py function for point size (yuch)
    text_style.SetFont(wx.Font(10,
                               wx.FONTFAMILY_MODERN,
                               wx.FONTSTYLE_NORMAL,
                               wx.FONTWEIGHT_NORMAL))
    self._text_ctrl.SetDefaultStyle(text_style)
    self._text_ctrl.SetClientSize(self.GetClientSize())
    self._PositionNewFrame()

  def _PositionNewFrame(self):
    """Set a new frame in the proper (_tiled) position."""
    self.Move(TextFrame._tile_position)
    self._ShiftTilePosition()

  @classmethod
  def _ResetTiling(cls):
    """Reset tiling to intial conditions (for testing)."""
    cls._tile_initial = cls._tile_initial_reset[:]
    cls._tile_position = cls._tile_initial[:]

  @classmethod
  def _ShiftTilePosition(cls):
    """Shift the window tile position so console windows don't overlap."""
    cls._tile_position = map(lambda x,dx: x+dx,
                             cls._tile_position,
                             cls._TILE_SKIP)
    # If too far off to the right/bottom, reset with an offset.
    (_, _, max_x, max_y) = wx.Display().GetClientArea()
    if cls._tile_position[1] > max_y:
      cls._tile_initial[0] += cls._TILE_SKIP[0]
      cls._tile_position = cls._tile_initial[:]
    if cls._tile_position[0] > max_x:
      cls._tile_initial[1] += cls._TILE_SKIP[1]
      cls._tile_position = cls._tile_initial[:]
    # possibly start over if, after reset, we're still too far
    if ((cls._tile_position[0] > max_x) or
        (cls._tile_position[1] > max_y)):
      cls._ResetTiling()

  def DisplayAndBringToFront(self):
    """Display the frame (if needed) and pop it to the front."""
    self.Show()
    # Docs say this is redundant for the 1st Show(), but not the 2nd one
    self.Raise()

  def AppendText(self, line):
    """Append text to our text control.

    This should be called in the main thread, so wx.CallAfter() might be useful.

    Args:
      line: a string of text to append.
    """
    self._text_ctrl.AppendText(line)

  def GetText(self):
    """Return our text control's full text.  For unittest convenience."""
    return self._text_ctrl.GetValue()
