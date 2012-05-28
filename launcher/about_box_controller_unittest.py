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
"""Unittests for about_box_controller.py"""

import unittest
import mox
import wx
import launcher

class AboutBoxControllerTest(unittest.TestCase):

  def setUp(self):
    # Must always create a wx.App first
    self.app = wx.PySimpleApp()

  def testGeneral(self):
    abc = launcher.AboutBoxController()
    # Make sure it looks like HTML in there
    text = abc._dialog.ToText()
    self.assertTrue(len(text) > 10)
    self.assertTrue(text.find('project manager'))
    # Check at least one substitution happened
    self.assertEquals(-1, text.find('{python-version}'))

  def testLink(self):
    def clicked(link):
      self.link = link
      return True
    abc = launcher.AboutBoxController()
    linkstring = 'http://www.google.com'
    linkinfo = wx.html.HtmlLinkInfo(linkstring)
    evt = wx.html.HtmlLinkEvent(-1, linkinfo)
    abc._OnLinkClicked(evt, browsefunc=clicked)
    linkinfo.Destroy()
    self.assertEqual(linkstring, self.link)


if __name__ == '__main__':
  unittest.main()
