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
del sys.path[0]

addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	scriptCategory = addonHandler.getCodeAddon().manifest["summary"]

	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		if globalVars.appArgs.secure:
			return
		self.createMenu()

	def createMenu(self):
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(AddonSettings)

	def terminate(self):
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(AddonSettings)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Reports elapsed time of current playback song (global)"),
	)
	def script_getSongElapsedTime(self, gesture):
		info = apiUtils.getSongElapsedTime()
		ui.message(info)

	@script(
		# Translators: Message presented in input help mode.
		description=_("Reports remaining time of current playback song (global)"),
	)
	def script_getSongRemainingTime(self, gesture):
		info = apiUtils.getSongRemainingTime()
		ui.message(info)


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
			ui.message(_("Please input a valid IP address"))
			textCtrl.SetFocus()
			textCtrl.Clear()
			textCtrl.Refresh()
			eventHandler.queueEvent("gainFocus", textCtrl)
			return False

	def TransferToWindow(self):
		return True

	def TransferFromWindow(self):
		return True


