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

"""Unittests for resizing_listctrl.py"""

import unittest
import wx
import launcher


class ResizingListCtrlTest(unittest.TestCase):
  """Exercise the Resizing ListCtrl class"""

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()
    ac = launcher.AppController(self.app)

  def testCreation(self):
    """Test object creation"""
    parent = wx.Frame(None)
    launcher.ResizingListCtrl(parent, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)


if __name__ == '__main__':
  unittest.main()
