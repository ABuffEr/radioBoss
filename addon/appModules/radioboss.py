# -*- coding: UTF-8 -*-
# RadioBOSS app module
# Copyright (C) 2024 Alberto Buffolino
# Released under GPL 2

import addonHandler
import appModuleHandler
import os
import sys
import ui

from controlTypes import Role as roles
from scriptHandler import script

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from radioBoss import apiUtils
del sys.path[0]

addonHandler.initTranslation()


class AppModule(appModuleHandler.AppModule):

	scriptCategory = addonHandler.getCodeAddon().manifest["summary"]

#	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
#		pass

	@script(
		# Translators: Message presented in input help mode.
		description=_("Enables/disables microphone, and reports it (app only)"),
		gesture="kb:F8"
	)
	def script_toggleMicStatus(self, gesture):
		gesture.send()
		status = apiUtils.getMicStatus()
		ui.message(status)

