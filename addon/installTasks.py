import addonHandler

from configobj import ConfigObj
from NVDAState import WritePaths

addonHandler.initTranslation()

def onInstall():
	import gui
	import wx
	for addon in addonHandler.getAvailableAddons():
		if addon.name == "radioBoss":
			if "1.0.2024" in addon.version or addon.version == "1.0.20250125":
				gui.messageBox(
					# Translators: the label of a message box dialog.
					_("Previous global gestures will be lost. Please configure them again, as app gestures."),
					# Translators: the title of a message box dialog.
					_("Add-on gestures reset!"),
					wx.OK|wx.ICON_WARNING)
				try:
					gestureClean()
				except:
					pass

def gestureClean():
	filename = WritePaths.gesturesConfigFile
	gestures = ConfigObj(filename, file_error=True, encoding="UTF-8")
	key = "globalPlugins.radioboss.GlobalPlugin"
	if gestures.get(key, False):
		del gestures[key]
		gestures.write()
