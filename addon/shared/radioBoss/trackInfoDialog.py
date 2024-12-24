# -*- coding: UTF-8 -*-
# RadioBOSS app module
# Copyright (C) 2024 Alberto Buffolino
# Released under GPL 2

import gui
import wx

from gui.guiHelper import BoxSizerHelper

class TrackInfoDialog(wx.Dialog):

	def __init__(self, title, details):
		super().__init__(None, title=title)
		helperSizer = BoxSizerHelper(self, wx.VERTICAL)
		choices = ["%s: %s"%(k.title(),v) for k,v in details.items() if v]
		infoList = helperSizer.addLabeledControl("", wx.ListBox, choices=choices)
		infoList.SetSelection(0 if len(choices) else -1)
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		mainSizer.Add(helperSizer.sizer, border=10, flag=wx.ALL)
		mainSizer.Fit(self)
		self.Bind(wx.EVT_CHAR_HOOK, self.onEscape)
		self.SetSizer(mainSizer)

	def onEscape(self, event):
		if event.GetKeyCode() == wx.WXK_ESCAPE:
			self.Destroy()
		else:
			event.Skip()

	@classmethod
	def Run(cls, title, details):
		gui.mainFrame.prePopup()
		d = cls(title, details)
		if d:
			d.Show()
		gui.mainFrame.postPopup()
