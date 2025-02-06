# -*- coding: UTF-8 -*-
# RadioBOSS app module
# Copyright (C) 2024 Alberto Buffolino
# Released under GPL 2

import addonHandler
import api
import appModuleHandler
import eventHandler
import globalPluginHandler
import globalVars
import gui
import os
import sys
import ui
import winUser
import wx

from ctypes import windll
from gui import guiHelper, nvdaControls, settingsDialogs
from ipaddress import ip_address
from scriptHandler import script

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))
from radioBoss import utils
from radioBoss.configManager import addonConfig
del sys.path[0]

addonHandler.initTranslation()

# to track and switch windows
rbWindowHandle = lastWindowHandle = None


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	scriptCategory = addonHandler.getCodeAddon().manifest["summary"]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if globalVars.appArgs.secure:
			return
		self.createMenu()
		appModuleHandler.post_appSwitch.register(self.trackWindow)

	def createMenu(self):
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(AddonSettings)

	def terminate(self):
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(AddonSettings)

	def trackWindow(self):
		global rbWindowHandle, lastWindowHandle
		obj = api.getForegroundObject()
		if hasattr(obj, "appModule") and obj.appModule and obj.appModule.appName == "radioboss":
			rbWindowHandle = obj.windowHandle
		elif windll.user32.IsWindowVisible(obj.windowHandle) and obj.windowClassName != "WorkerW":  # exclude desktop, that causes problems
			lastWindowHandle = obj.windowHandle

	@script(
		# Translators: Message presented in input help mode.
		description=_("Switches between RadioBOSS and other windows where you are (global)"),
	)
	def script_switchWindow(self, gesture):
		obj = api.getForegroundObject()
		if hasattr(obj, "appModule") and obj.appModule and obj.appModule.appName == "radioboss":
			errMsg = _("Unable to switch to previous window")
			handle = lastWindowHandle
		else:
			errMsg = _("Unable to switch to RadioBOSS window")
			handle = rbWindowHandle
		if not handle:
			ui.message(errMsg)
			return
		res = windll.user32.SwitchToThisWindow(handle, True) if windll.user32.IsWindowVisible(handle) else 0
		if not res:
			ui.message(errMsg)


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

