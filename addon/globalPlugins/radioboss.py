# -*- coding: UTF-8 -*-
# RadioBOSS app module
# Copyright (C) 2024 Alberto Buffolino
# Released under GPL 2

import addonHandler
import eventHandler
import globalPluginHandler
import globalVars
import gui
import os
import sys
import ui
import wx

from ipaddress import ip_address
from gui import guiHelper, nvdaControls, settingsDialogs
from scriptHandler import script

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from radioBoss import apiUtils, utils
from radioBoss.configManager import addonConfig
from radioBoss.constants import TrackDetails
from radioBoss.trackInfoDialog import TrackInfoDialog
del sys.path[0]

addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	scriptCategory = addonHandler.getCodeAddon().manifest["summary"]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if globalVars.appArgs.secure:
			return
		self.createMenu()

	def createMenu(self):
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(AddonSettings)

	def terminate(self):
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(AddonSettings)

	@classmethod
	def addTrackDetailScript(cls, detail):
		scriptSuffix = detail.title()
		scriptName = "getCurrentTrack%s" % scriptSuffix
		funcName = "script_%s" % scriptName
		script = lambda self, gesture: self.reportCurrentTrackDetail(detail)
		# Translators: Message presented in input help mode.
		description = _("Reports {detail} of the current track (global)")
		script.__doc__ = description.format(detail=detail.lower())
		script.__name__ = funcName
		setattr(cls, funcName, script)

	def reportCurrentTrackDetail(self, detail):
		info = apiUtils.getCurrentTrackInfo(detail)
		ui.message(info)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Reports elapsed time of the current track (global)"),
	)
	def script_getSongElapsedTime(self, gesture):
		info = apiUtils.getSongElapsedTime()
		ui.message(info)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Reports remaining time of the current track (global)"),
	)
	def script_getSongRemainingTime(self, gesture):
		info = apiUtils.getSongRemainingTime()
		ui.message(info)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Reports remaining time of the playlist (global)"),
	)
	def script_getPlaylistRemainingTime(self, gesture):
		info = apiUtils.getPlaylistRemainingTime()
		ui.message(info)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Views in a dialog all details of the current track (global)"),
	)
	def script_viewCurrentTrackInfo(self, gesture):
		details = apiUtils.getFullCurrentTrackInfo()
		if isinstance(details, str): # something went wrong
			ui.message(details)
			return
		wx.CallAfter(
			TrackInfoDialog.Run,
			title=_("Details of the current track"),
			details=details
		)


register = GlobalPlugin.addTrackDetailScript
for detail in list(TrackDetails):
	register(detail)


class AddonSettings(settingsDialogs.SettingsPanel):
	"""Class to define settings."""

	title = addonHandler.getCodeAddon().manifest["summary"]

	def makeSettings(self, settingsSizer):
		settingsSizerHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: label for protocol in settings
		protocolLabelText = _("Protocol:")
		protocolChoices = ("http", "https")
		self.protocolCombo = settingsSizerHelper.addLabeledControl(
			protocolLabelText,
			wx.Choice,
			choices=protocolChoices
		)
		self.protocolCombo.SetStringSelection(addonConfig["protocol"])
		# Translators: label for host IP in settings
		hostLabelText = _("Host IP:")
		self.hostEdit = settingsSizerHelper.addLabeledControl(
			hostLabelText,
			wx.TextCtrl,
		)
		self.hostEdit.SetValue(addonConfig["host"])
		self.hostEdit.SetValidator(IPValidator())
		# Translators: label for port in settings
		portLabelText = _("Port:")
		self.portEdit = settingsSizerHelper.addLabeledControl(
			portLabelText,
			nvdaControls.SelectOnFocusSpinCtrl,
			min=1025,
			max=65535,
			initial=addonConfig["port"]
		)
		# Translators: label for password in settings
		passwordLabelText = _("Password:")
		self.passwordEdit = settingsSizerHelper.addLabeledControl(passwordLabelText, wx.TextCtrl)
		encodedPwd = addonConfig["password"]
		clearPwd = utils.decodeBase64String(encodedPwd)
		self.passwordEdit.SetValue(clearPwd)

	def onSave(self):
		# Update Configuration
		addonConfig["protocol"] = self.protocolCombo.GetStringSelection()
		addonConfig["host"] = self.hostEdit.GetValue()
		addonConfig["port"] = self.portEdit.GetValue()
		clearPwd = self.passwordEdit.GetValue()
		encodedPwd = utils.encodeBase64String(clearPwd)
		addonConfig["password"] = encodedPwd


class IPValidator(wx.Validator):

	def __init__(self):
		super().__init__()
		self.Bind(wx.EVT_KILL_FOCUS, self.onLoseFocus)

	def Clone(self):
		return IPValidator()

	def onLoseFocus(self, evt):
		self.Validate()

	def Validate(self, win=None):
		textCtrl = self.GetWindow()
		text = textCtrl.GetValue()
		try:
			ip_address(text)
			return True
		except ValueError:
			ui.message(_("Please enter a valid IP address"))
			textCtrl.SetFocus()
			textCtrl.Clear()
			textCtrl.Refresh()
			eventHandler.queueEvent("gainFocus", textCtrl)
			return False

	def TransferToWindow(self):
		return True

	def TransferFromWindow(self):
		return True


