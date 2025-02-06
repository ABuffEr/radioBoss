# -*- coding: UTF-8 -*-
# RadioBOSS app module
# Copyright (C) 2024 Alberto Buffolino
# Released under GPL 2

import appModuleHandler

from controlTypes import Role as roles

from .radioboss import BaseAppModule


class AppModule(BaseAppModule, appModuleHandler.AppModule):

	def event_gainFocus(self, obj, nextHandler):
		if not obj.name and obj.windowClassName == "TSpinFloatEdit":
			obj.name = obj.simplePrevious.name if obj.simplePrevious.role == roles.CHECKBOX else obj.simpleNext.name
			nextHandler()
		else:
			super().event_gainFocus(obj, nextHandler)
