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

"""ListCtrl that automatically resizes the path column"""

import wx
import wx.lib.mixins.listctrl as listmixin


class ResizingListCtrl(wx.ListCtrl, listmixin.ListCtrlAutoWidthMixin):

  def __init__(self, parent, ID, pos=wx.DefaultPosition,
               size=wx.DefaultSize, style=0):
    wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

    listmixin.ListCtrlAutoWidthMixin.__init__(self)
    self.setResizeColumn(3)  # the "path" column
