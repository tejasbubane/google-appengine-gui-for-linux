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
"""Unittests for html_info_dialog.py"""

import unittest
import mox
import wx
import launcher

class HtmlInfoDialogTest(unittest.TestCase):

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()

  def testCreate(self):
    hidt = launcher.HtmlInfoDialog(None, -1)
    sizer = hidt.GetSizer()
    children = sizer.GetChildren()
    types = map(lambda x: type(x.GetWindow()), children)
    self.assertTrue(wx.Button in types)
    self.assertTrue(wx.html.HtmlWindow in types)

  def testSetPage(self):
    hidt = launcher.HtmlInfoDialog(None, -1)
    for text in ('<b>hi dave</b>', '<i>thanks for the code reviews</i>'):
      hidt.SetPage(text)
      self.assertTrue(text, hidt.ToText())

  def testBindOK(self):
    hidt = launcher.HtmlInfoDialog(None, -1)
    def hitfunc(x):
      self.button_hit = True
    hidt.BindOK(hitfunc)
    self.button_hit = False
    button = hidt._ok_button
    evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, button.GetId())
    button.ProcessEvent(evt)
    self.assertTrue(self.button_hit)
    pass

  def testBindLink(self):
    # TODO(jrg):
    # For clicking on a link, there is no window involved for us to
    # post/process an event on to simulate the click.  So how can I
    # test this?
    pass


if __name__ == '__main__':
  unittest.main()
