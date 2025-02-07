# -*- coding: UTF-8 -*-
# RadioBOSS app module
# Copyright (C) 2024 Alberto Buffolino
# Released under GPL 2

import appModuleHandler

from controlTypes import Role as roles

from .radioboss import BaseAppModule, labelAutofinder


class AppModule(BaseAppModule, appModuleHandler.AppModule):

	def event_gainFocus(self, obj, nextHandler):
		if not obj.name and obj.role == roles.EDITABLETEXT and obj.simpleParent.windowClassName == "TTabSheet":
			obj.name = labelAutofinder.getLabel(obj=obj, searchDirections=labelAutofinder.SearchDirections.RIGHT, maxHorizontalDistance=32)
			nextHandler()
		else:
			return super().event_gainFocus(obj, nextHandler)
