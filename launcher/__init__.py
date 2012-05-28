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

# "import *" violates Google style rules.  However, the launcher
# project isn't expected to be more than ~25 classes, and is quite
# independent of other python use, so namespace collision shouldn't be
# a problem.  Stylistic correctness ("import app", and use as
# launcher.app.App instead of launcher.App) is a bit wordy here.
#
# Interestingly, many 3rd party packages in use at Google (such as
# Django and wx) use the "import *" construct.

from app import *
from about_box_controller import *
from addexisting_controller import *
from addnew_controller import *
from appcontroller import *
from deploy_controller import *
from dev_appserver_task_thread import *
from dialoghandler import *
from dialog_controller_base import *
from html_info_dialog import *
from log_console import *
from mainframe import *
from mainframe_selection_helper import *
from maintable import *
from platform import *
from prefcontroller import *
from preferences import *
from preferenceview import *
from project import *
from resizing_listctrl import *
from runtime import *
from settings_controller import *
from taskcontroller import *
from taskthread import *
from text_frame import *

