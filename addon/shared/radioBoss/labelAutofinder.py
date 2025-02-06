# -*- coding: UTF-8 -*-
# LabelAutofinder module/add-on
# Copyright (C) 2025 Alberto Buffolino
# Released under GPL 2

import api

from controlTypes import Role as roles
from displayModel import DisplayModelTextInfo as DMTI

# to enable debug
DEBUG = False

def getLabel(obj=None, textObj=None, breakObj=None, searchDirections=None):
	# it's better to provide obj, e.g. via event_* filtering, but anyway...
	if not obj:
		obj = api.getFocusObject()
	# get text from obj that contains it (textObj), provided or discovered automatically
	info = getTextFromContainer(obj, textObj, breakObj)
	if not info:
		debugLog("No text found!")
		return
	if not searchDirections:
		# labels are usally at the top or on the left
		searchDirections = SearchDirections.TOP_LEFT
	# rectangle of obj to label, in (left, top, right, bottom) representation
	# Remember:
	# x (left and right coordinates) goes from 0 to positive integers,
	# moving from left to right on the screen;
	# y (top and bottom coordinates) does the same but
	# moving from top to bottom on the screen;
	objRect = obj.location.toLTRB()
	# max distance between an obj point (left and right) and its outside neighbor
	maxHorizontalDistance = RestrictedDMTI.minHorizontalWhitespace
	# explorer that looks around obj
	explorer = BoundingExplorer(objRect, maxHorizontalDistance, searchDirections)
	# rectangles for each char in textObj
	charRects = info._storyFieldsAndRects[1]
	# get possible offsets of label
	charOffsets = explorer.getCharOffsets(charRects)
	if not charOffsets:
		debugLog("No chars around obj!")
		return
	# calculate a mean of found offsets, to avoid spurious results
	chunkCenterOffset = sum(charOffsets)//len(charOffsets)
	# get start and end offsets for whole label
	labelStartOffset, labelEndOffset = info._getDisplayChunkOffsets(chunkCenterOffset)
	# finally, get label text from textObj
	labelText = info.text[labelStartOffset:labelEndOffset]
	debugLog("Label: %s"%labelText)
	return labelText

def getTextFromContainer(obj, textObj, breakObj):
	# breakObj is the topmost limit for textObj search
	if not breakObj:
		breakObj = api.getForegroundObject()
	# find a textObj in obj ancestors that could provide labels
	info = None
	ancestors = [textObj] if textObj else getAncestors(obj)
	for ancestor in reversed(ancestors):
		# useful to avoid obj parent that would provide obj content as text
		if ancestor.windowHandle != obj.windowHandle:
			# get text restricted to that ancestor, without children
			tempInfo = RestrictedDMTI(ancestor, ancestor.location.toLTRB())
			if tempInfo.text:
				info = tempInfo
#				debugLog("Found textObj: %s\nwith text: %s"%(ancestor.devInfo, info.text))
				break
		if ancestor == breakObj:
			break
	return info

def getAncestors(obj):
	parents = []
	while (parent := obj.parent):
		parents.append(parent)
		obj = parent
	return list(reversed(parents))


# class to exclude children from text retrieval
class RestrictedDMTI(DMTI):

	includeDescendantWindows = False


# class to collect useful search direction tuples
class SearchDirections:

	LEFT = (0,)
	TOP = (1,)
	RIGHT = (2,)
	BOTTOM = (3,)
	TOP_LEFT = (*TOP, *LEFT)
	LEFT_BOTTOM = (*LEFT, *BOTTOM)
	BOTTOM_RIGHT = (*BOTTOM, *RIGHT)
	RIGHT_TOP = (*RIGHT, *TOP)
	ALL = (*LEFT, *TOP, *RIGHT, *BOTTOM)


# solution core: explorer of obj neighborhood
class BoundingExplorer:

	def __init__(self, objRect, maxHorizontalDistance, searchDirections):
		# obj rectangle which you look around
		self.objRect = objRect
		# max external distance from an obj point (left or right)
		self.maxHorizontalDistance = maxHorizontalDistance
		# methods for checking on each direction
		checkerMethods = (self.leftCheck, self.topCheck, self.rightCheck, self.bottomCheck)
		# char offsets collected for each direction
		self.offsets = {}
		# char distances collected for each direction
		self.distances = {}
		# checker methods to be invoke (according to passed directions)
		self.checkers = {}
		# initialize  for each passed direction
		for direction, checker in enumerate(checkerMethods):
			if direction in searchDirections:
				self.offsets[direction] = []
				self.distances[direction] = []
				self.checkers[direction] = checker

	def getCharOffsets(self, charRects):
		debugLog("Rects to analyze: %d"%len(charRects))
		# check proximity and distance
		# for each char rect around obj
		# in specified directions,
		# saving offset and distance if compatible
		for offset, charRect in enumerate(charRects):
			for direction, checker in self.checkers.items():
				distance = checker(charRect)
				if distance:
					self.offsets[direction].append(offset)
					self.distances[direction].append(distance)
		if not any(self.offsets.values()):
			debugLog("No chunk offset found!")
			return
		# establish best direction to consider
		chosenDirection = self.chooseDirection()
		if chosenDirection is None:
			debugLog("No direction found!")
			return
		debugLog("Chosen direction: %s"%chosenDirection)
		# and return the collected offsets in that direction
		return self.offsets[chosenDirection]

	def chooseDirection(self):
		# calculate average distance in specified directions
		# or set a no-sense, giant one instead (when no offsets)
		avgDistances = {}
		for direction in self.checkers.keys():
			distances = self.distances[direction]
			avgDistance = sum(distances)//len(distances) if distances else 10000
			avgDistances[direction] = avgDistance
		# get direction with minimum average distance
		# and check whether it's valid
		chosenDirection = min(avgDistances, key=avgDistances.get)
		minDistance = avgDistances[chosenDirection]
		if minDistance == 10000:
			debugLog("Unable to establish label position")
			return
		debugLog("Min distance: %d"%minDistance)
		# return best direction where retrieve offsets
		return chosenDirection

	def leftCheck(self, charRect):
		objLeft, objTop, objRight, objBottom = self.objRect
		charLeft, charTop, charRight, charBottom = charRect
		if (
			(objTop<charBottom<=objBottom)
			and
			(objLeft > charRight)
			and
			(objLeft-charRight <= self.maxHorizontalDistance)
		):
			distance = objLeft-charRight
			return distance

	def topCheck(self, charRect):
		objLeft, objTop, objRight, objBottom = self.objRect
		charLeft, charTop, charRight, charBottom = charRect
		charHeight = charRect.height
		if (
			(objLeft<=charLeft<objRight)
			and
			(objTop > charBottom)
			and
			(objTop-charBottom <= charHeight)
		):
			distance = objTop-charBottom
			return distance

	def rightCheck(self, charRect):
		objLeft, objTop, objRight, objBottom = self.objRect
		charLeft, charTop, charRight, charBottom = charRect
		if (
			(objTop<charBottom<=objBottom)
			and
			(charLeft > objRight)
			and
			(charLeft-objRight <= self.maxHorizontalDistance)
		):
			distance = charLeft-objRight
			return distance

	def bottomCheck(self, charRect):
		objLeft, objTop, objRight, objBottom = self.objRect
		charLeft, charTop, charRight, charBottom = charRect
		charHeight = charRect.height
		if (
			(objLeft<=charLeft<objRight)
			and
			(charTop > objBottom)
			and
			(charTop-objBottom <= charHeight)
		):
			distance = charTop-objBottom
			return distance


# useful minor methods

# for logging
from logHandler import log

def debugLog(message):
	if DEBUG:
		log.info(message)

# for testing performances
import time
from contextlib import contextmanager

@contextmanager
def measureTime(label):
	start = time.time()
	try:
		yield
	finally:
		end = time.time()
		debugLog("%s: %.3f s"%(label, end-start))

# for forcing obj to correctly refresh its text content,
# useful in some (Delphi?) software;
# see SetWindowPos documentation:
# https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowpos
from ctypes import windll

SWP_FRAMECHANGED = 0x0020
SWP_NOCOPYBITS = 0x0100
SWP_NOMOVE = 0x0002
SWP_NOREPOSITION = 0x0200
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_SHOWWINDOW = 0x0040
# join together
SWP_FLAGS = SWP_FRAMECHANGED|SWP_NOCOPYBITS|SWP_NOMOVE|SWP_NOREPOSITION|SWP_NOSIZE|SWP_NOZORDER|SWP_SHOWWINDOW

def refreshTextContent(obj):
	windll.user32.SetWindowPos(obj.windowHandle, None, None, None, None, None, SWP_FLAGS)
