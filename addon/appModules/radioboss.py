# -*- coding: UTF-8 -*-
# RadioBOSS app module
# Copyright (C) 2024 Alberto Buffolino
# Released under GPL 2

import addonHandler
import api
import appModuleHandler
import os
import speech
import sys
import ui
import wx

from controlTypes import Role as roles
from scriptHandler import script

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from radioBoss import apiUtils, labelAutofinder
from radioBoss.constants import TrackDetails
from radioBoss.trackInfoDialog import TrackInfoDialog
del sys.path[0]

addonHandler.initTranslation()


class BaseAppModule:

	def event_foreground(self, obj, nextHandler):
		if obj.role == roles.PANE and obj.windowClassName in ("TLibraryFrm", "TTagEditFrm", "TForm2"):
			obj.redraw()
			speech.speak(obj.name)
		nextHandler()

	def event_gainFocus(self, obj, nextHandler):
		# avoid None obj
		if not obj:
			return
		if (
			(not obj.name)
			and
			(obj.role == roles.COMBOBOX or (obj.role == roles.EDITABLETEXT and obj.simpleParent.role != roles.COMBOBOX))
		):
			obj.name = labelAutofinder.getLabel(obj=obj)
		nextHandler()

	def event_focusEntered(self, obj, nextHandler):
		if not obj:
			return
		if not obj.name and obj.role == roles.COMBOBOX:
			obj.name = labelAutofinder.getLabel(obj=obj)
		nextHandler()


class AppModule(BaseAppModule, appModuleHandler.AppModule):

	scriptCategory = addonHandler.getCodeAddon().manifest["summary"]

	@classmethod
	def addTrackDetailScript(cls, detail):
		scriptSuffix = detail.title()
		scriptName = "getPosTrack%s" % scriptSuffix
		funcName = "script_%s" % scriptName
		script = lambda self, gesture: self.reportPosTrackDetail(detail)
		# Translators: Message presented in input help mode.
		description = _("Reports {detail} of the track at focused position in the playlist (app only)")
		script.__doc__ = description.format(detail=detail.lower())
		script.__name__ = funcName
		script.speakOnDemand = True
		setattr(cls, funcName, script)

	def reportPosTrackDetail(self, detail):
		pos = self.getTrackPos()
		if not pos:
			return
		info = apiUtils.getPosTrackInfo(pos, detail)
		ui.message(info)

	def getTrackPos(self):
		curItem = api.getFocusObject()
		if curItem.role != roles.TREEVIEWITEM and curItem.windowClassName != "TVirtualTreePlaylist":
			ui.message(_("No playlist treeview found"))
			return
		pos = None
		try:
			posRow = curItem.name.split(";", 1)[0]
			pos = int(posRow)
		except:
			pass
		if not pos:
			info = _("Unable to get the track position from first column, please see documentation.")
			ui.message(info)
		return pos

	@script(
		# Translators: Message presented in input help mode.
		description=_("Enables/disables microphone, and reports it (app only)"),
		gesture="kb:F8",
		speakOnDemand=True
	)
	def script_toggleMicStatus(self, gesture):
		gesture.send()
		status = apiUtils.getMicStatus()
		ui.message(status)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Views in a dialog all details of the track at focused position in the playlist (app only)"),
		speakOnDemand=True
	)
	def script_viewPosTrackInfo(self, gesture):
		pos = self.getTrackPos()
		if not pos:
			return
		details = apiUtils.getFullPosTrackInfo(pos)
		if isinstance(details, str): # something went wrong
			ui.message(details)
			return
		wx.CallAfter(
			TrackInfoDialog.Run,
			title=_("Details of track {pos}").format(pos=pos),
			details=details
		)


register = AppModule.addTrackDetailScript
for detail in list(TrackDetails):
	register(detail)
