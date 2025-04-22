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
from NVDAObjects.IAccessible import IAccessible, getNVDAObjectFromEvent
from scriptHandler import script
from windowUtils import findDescendantWindow

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from labelAutofinderCore import getLabel, SearchConfig, SearchDirections, refreshTextContent
from radioBoss import apiUtils
from radioBoss.configManager import addonConfig
from radioBoss.constants import TrackDetails
from radioBoss.trackInfoDialog import TrackInfoDialog
del sys.path[0]
del sys.modules["labelAutofinderCore"]
del sys.modules["radioBoss"]

addonHandler.initTranslation()


class BaseAppModule:

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		# to fix slider accessibility
		if not obj.name and obj.role == roles.SLIDER:
			clsList.insert(0, SliderWithUnit)

	def event_foreground(self, obj, nextHandler):
		# to fix text disappearing
		if obj.role == roles.PANE:
			refreshTextContent(obj)
		nextHandler()

	def event_gainFocus(self, obj, nextHandler):
		# avoid None obj
		if not obj:
			return
		# to label simple edit and combo boxes
		if (
			(not obj.name)
			and
			(obj.role == roles.COMBOBOX or (obj.role == roles.EDITABLETEXT and obj.simpleParent.role != roles.COMBOBOX))
			and
			(obj.location and obj.location.width < 300)
		):
			obj.name = getLabel(obj)
		nextHandler()

	def event_focusEntered(self, obj, nextHandler):
		# avoid None obj
		if not obj:
			return
		# to label combo with edit boxes
		if not obj.name and obj.role == roles.COMBOBOX:
			obj.name = getLabel(obj)
		nextHandler()


class AppModule(BaseAppModule, appModuleHandler.AppModule):

	summary = addonHandler.getCodeAddon().manifest["summary"]
	availability = _("(app only)")
	scriptCategory = ' '.join([summary, availability])

	@classmethod
	def addPosTrackDetailScript(cls, detail):
		scriptSuffix = detail.title()
		scriptName = "getPosTrack%s" % scriptSuffix
		funcName = "script_%s" % scriptName
		script = lambda self, gesture: self.reportPosTrackDetail(detail)
		# Translators: Message presented in input help mode.
		description = _("Reports {detail} of the track at focused position in the playlist")
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
		description=_("Enables/disables microphone, and reports it"),
		gesture="kb:F8",
		speakOnDemand=True
	)
	def script_toggleMicStatus(self, gesture):
		gesture.send()
		status = apiUtils.getMicStatus()
		ui.message(status)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Views in a dialog all details of the track at focused position in the playlist"),
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

	@classmethod
	def addCurrentTrackDetailScript(cls, detail):
		scriptSuffix = detail.title()
		scriptName = "getCurrentTrack%s" % scriptSuffix
		funcName = "script_%s" % scriptName
		script = lambda self, gesture: self.reportCurrentTrackDetail(detail)
		# Translators: Message presented in input help mode.
		description = _("Reports {detail} of the current track")
		script.__doc__ = description.format(detail=detail.lower())
		script.__name__ = funcName
		script.speakOnDemand = True
		setattr(cls, funcName, script)

	def reportCurrentTrackDetail(self, detail):
		info = apiUtils.getCurrentTrackInfo(detail)
		ui.message(info)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Reports elapsed time of the current track"),
		speakOnDemand=True
	)
	def script_getSongElapsedTime(self, gesture):
		info = apiUtils.getSongElapsedTime()
		ui.message(info)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Reports remaining time of the current track"),
		speakOnDemand=True
	)
	def script_getSongRemainingTime(self, gesture):
		info = apiUtils.getSongRemainingTime()
		ui.message(info)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Reports remaining time of the playlist"),
		speakOnDemand=True
	)
	def script_getPlaylistRemainingTime(self, gesture):
		info = apiUtils.getPlaylistRemainingTime()
		ui.message(info)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Views in a dialog all details of the current track"),
		speakOnDemand=True
	)
	def script_viewCurrentTrackInfo(self, gesture):
		details = apiUtils.getPlaybackTrackInfo("current")
		if isinstance(details, str): # something went wrong
			# Translators: error if info of current track is not available
			ui.message(_("No current track"))
			return
		wx.CallAfter(
			TrackInfoDialog.Run,
			title=_("Details of the current track"),
			details=details
		)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Report a summary of previous track info"),
		speakOnDemand=True
	)
	def script_previousTrackSummary(self, gesture):
		details = [detail.upper() for detail in addonConfig["infoSummary"]]
		info = apiUtils.getPlaybackTrackInfo("previous", details)
		if isinstance(info, str) or not any(info.values()): # something went wrong
			# Translators: error if summary of previous track is not available
			ui.message(_("No previous track"))
			return
		msg = ""
		for k, v in info.items():
			tempMsg = "%s: %s; "%(k.title(), v)
			msg = ''.join([msg, tempMsg])
		ui.message(msg)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Report a summary of current track info"),
		speakOnDemand=True
	)
	def script_currentTrackSummary(self, gesture):
		details = [detail.upper() for detail in addonConfig["infoSummary"]]
		info = apiUtils.getPlaybackTrackInfo("current", details)
		if isinstance(info, str) or not any(info.values()): # something went wrong
			# Translators: error if summary of current track is not available
			ui.message(_("No current track"))
			return
		msg = ""
		for k, v in info.items():
			tempMsg = "%s: %s; "%(k.title(), v)
			msg = ''.join([msg, tempMsg])
		ui.message(msg)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Report a summary of next track info"),
		speakOnDemand=True
	)
	def script_nextTrackSummary(self, gesture):
		details = [detail.upper() for detail in addonConfig["infoSummary"]]
		info = apiUtils.getPlaybackTrackInfo("next", details)
		if isinstance(info, str) or not any(info.values()): # something went wrong
			# Translators: error if summary of next track is not available
			ui.message(_("No next track"))
			return
		msg = ""
		for k, v in info.items():
			tempMsg = "%s: %s; "%(k.title(), v)
			msg = ''.join([msg, tempMsg])
		ui.message(msg)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Jumps to log events"),
		speakOnDemand=True
	)
	def script_jumpToLog(self, gesture):
		fg = api.getForegroundObject()
		handle = findDescendantWindow(parent=fg.windowHandle, controlID=0, visible=True, className="TVirtualTreeLog")
		if not handle:
			ui.message(_("No log found"))
			return
		obj = getNVDAObjectFromEvent(handle, 0, 0)
		obj.setFocus()

	@script(
		# Translators: Message presented in input help mode.
		description=_("Jumps to playlist tree"),
		speakOnDemand=True
	)
	def script_jumpToPlaylist(self, gesture):
		fg = api.getForegroundObject()
		handle = findDescendantWindow(parent=fg.windowHandle, visible=True, controlID=0, className="TVirtualTreePlaylist")
		if not handle:
			ui.message(_("No playlist found"))
			return
		obj = getNVDAObjectFromEvent(handle, 0, 0)
		obj.setFocus()


posRegister = AppModule.addPosTrackDetailScript
currentRegister = AppModule.addCurrentTrackDetailScript
for detail in list(TrackDetails):
	posRegister(detail)
	currentRegister(detail)


class SliderWithUnit(IAccessible):

	def _get_name(self):
		name = getLabel(self)
		return name

	def _get_value(self):
		config = SearchConfig(directions=SearchDirections.RIGHT)
		value = getLabel(self, config)
		if not self._get_name():
			refreshTextContent(self.parent)
			self._get_name()
		return value
