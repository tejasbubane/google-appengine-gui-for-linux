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

import logging
import wx
import launcher


class DialogHandler(logging.Handler):
  """A logging handler to display log records in a wx modal dialog.

  Example setup:
    handler = launcher.DialogHandler(level=logging.WARNING)
    logging.getLogger('').addHandler(handler)

  Example use to log a warning in a modal dialog:
    import logging
    logging.warning('hello from a modal dialog')
  """

  def emit(self, record):
    """Required override of logging.Handler.emit()"""
    wx.MessageBox(record.getMessage(),
                  record.levelname.title(),
                  style=wx.CENTRE|wx.OK|wx.ICON_ERROR)
