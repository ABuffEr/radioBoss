# -*- coding: UTF-8 -*-
# LabelAutofinder module/add-on
# Copyright (C) 2025 Alberto Buffolino
# Released under GPL 2

import api
import winUser
import sys

from controlTypes import Role as roles
from displayModel import DisplayModelTextInfo as DMTI
from NVDAObjects.IAccessible import getNVDAObjectFromEvent

# to enable debug
DEBUG = False


def getLabel(*args, **kwargs):
	fg = api.getForegroundObject()
	staticHandles = getAllStaticHandles(fg.windowHandle)
	if staticHandles:
		return getRoleLabel(*args, **kwargs)
	else:
		return getTextLabel(*args, **kwargs)

def getRoleLabel(obj=None, maxParent=None, searchDirections=None, maxHorizontalDistance=150, maxVerticalDistance=150, overview=False):
	# it's better to provide obj, e.g. via event_* filtering, but anyway...
	if not obj:
		obj = api.getFocusObject()
	if not maxParent:
		maxParent = api.getForegroundObject()
	staticHandles = getAllStaticHandles(maxParent.windowHandle)
	if not staticHandles:
		debugLog("No handles found!")
		return
	objRect = obj.location.toLTRB()
	if not searchDirections:
		# labels are usally at the top or on the left
		searchDirections = SearchDirections.TOP_LEFT
	fg = api.getForegroundObject()
	if maxHorizontalDistance == sys.maxsize:
		maxHorizontalDistance = fg.location.width
	if maxVerticalDistance == sys.maxsize:
		maxVerticalDistance = fg.location.height
	# explorer that looks around obj
	explorer = StarExplorer(objRect, searchDirections, maxHorizontalDistance, maxVerticalDistance)
	staticObjs = [getNVDAObjectFromEvent(handle, winUser.OBJID_CLIENT, 0) for handle in staticHandles]
	res = explorer.getDistanceAndLabelText(staticObjs)
	if not res:
		return
	if overview:
		return res
	else:
		distance, label = res
		return label


def getTextLabel(obj=None, textObj=None, maxParent=None, searchDirections=None, maxHorizontalDistance=None, maxVerticalDistance=None, overview=False):
	# it's better to provide obj, e.g. via event_* filtering, but anyway...
	if not obj:
		obj = api.getFocusObject()
	# get text from obj that contains it (textObj), provided or discovered automatically
	info = getTextFromContainer(obj, textObj, maxParent)
	if not info:
		debugLog("No text found!")
		return
	# rectangle of obj to label, in (left, top, right, bottom) representation
	# Remember:
	# x (left and right coordinates) goes from 0 to positive integers,
	# moving from left to right on the screen;
	# y (top and bottom coordinates) does the same but
	# moving from top to bottom on the screen;
	objRect = obj.location.toLTRB()
	if not searchDirections:
		# labels are usally at the top or on the left
		searchDirections = SearchDirections.TOP_LEFT
	# max horizontal distance between an obj point (left and right) and its outside neighbor
	if not maxHorizontalDistance:
		maxHorizontalDistance	= RestrictedDMTI.minHorizontalWhitespace
	if maxHorizontalDistance == sys.maxsize:
		maxHorizontalDistance	= 10000
	if maxVerticalDistance == sys.maxsize:
		maxVerticalDistance = 10000
	# explorer that looks around obj
	explorer = BoundingExplorer(objRect, searchDirections, maxHorizontalDistance, maxVerticalDistance)
	# rectangles for each char in textObj
	charRects = info._storyFieldsAndRects[1]
	# get possible offsets of label
	res = explorer.getDistanceAndCharOffsets(charRects)
	if not res:
		debugLog("No chars around obj!")
		return
	distance, charOffsets	= res
	# calculate a mean of found offsets, to avoid spurious results
	chunkCenterOffset = sum(charOffsets)//len(charOffsets)
	# get start and end offsets for whole label
	labelStartOffset, labelEndOffset = info._getDisplayChunkOffsets(chunkCenterOffset)
	# finally, get label text from textObj
	label = info.text[labelStartOffset:labelEndOffset]
	debugLog("Label: %s"%label)
	if overview:
		return (distance, label)
	else:
		return label

def getTextFromContainer(obj, textObj, maxParent):
	# maxParent is the topmost limit for textObj search
	if not maxParent:
		maxParent = api.getForegroundObject()
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
				break
		if ancestor == maxParent:
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
	HORIZONTAL = (*LEFT, *RIGHT)
	VERTICAL = (*TOP, *BOTTOM)
	ALL = (*LEFT, *TOP, *RIGHT, *BOTTOM)


# solution core: explorer of obj neighborhood
class BoundingExplorer:

	def __init__(self, objRect, searchDirections, maxHorizontalDistance, maxVerticalDistance):
		# obj rectangle which you look around
		self.objRect = objRect
		# max external distance from an obj point (left or right)
		self.maxHorizontalDistance = maxHorizontalDistance
		# max external distance from an obj point (top or bottom)
		self.maxVerticalDistance = maxVerticalDistance
		# methods for checking on each direction
		checkerMethods = (self.leftCheck, self.topCheck, self.rightCheck, self.bottomCheck)
		# char distances and offsets collected for each direction
		self.distancesAndOffsets = {}
		# checker methods to be invoke (according to passed directions)
		self.checkers = {}
		# initialize  for each passed direction
		for direction, checker in enumerate(checkerMethods):
			if direction in searchDirections:
				self.distancesAndOffsets[direction] = {}
				self.checkers[direction] = checker

	def getDistanceAndCharOffsets(self, charRects):
		debugLog("Rects to analyze: %d"%len(charRects))
		# check proximity and distance
		# for each char rect around obj
		# in specified directions,
		# saving offset and distance if compatible
		for offset, charRect in enumerate(charRects):
			for direction, checker in self.checkers.items():
				distance = checker(charRect)
				if distance:
					self.distancesAndOffsets[direction].setdefault(distance, []).append(offset)
		if not any(self.distancesAndOffsets.values()):
			debugLog("No chunk offset found!")
			return
		# establish best direction to consider
		distanceAndDirection = self.getDistanceAndDirection()
		if not distanceAndDirection:
			debugLog("No direction found!")
			return
		distance, chosenDirection = distanceAndDirection
		debugLog("Chosen direction: %s"%chosenDirection)
		# and return min distance and the collected offsets in that direction
		offsets = self.distancesAndOffsets[chosenDirection][distance]
		return (distance, offsets)

	def getDistanceAndDirection(self):
		# find minimum distance in specified directions
		# or set a no-sense, giant one instead (when no offsets)
		minDistanceInDirection = {}
		for direction in self.checkers.keys():
			distances = self.distancesAndOffsets[direction].keys()
			minDistanceInDirection[direction] = min(distances) if distances else 10000
		# get direction with minimum distance
		# and check whether it's valid
		chosenDirection = min(minDistanceInDirection, key=minDistanceInDirection.get)
		minDistance = minDistanceInDirection[chosenDirection]
		if minDistance == 10000:
			debugLog("Unable to establish label position")
			return
		debugLog("Min distance: %d"%minDistance)
		# return best direction where retrieve offsets
		return (minDistance, chosenDirection)

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
		maxVerticalDistance = self.maxVerticalDistance if self.maxVerticalDistance else charRect.height
		if (
			(objLeft<=charLeft<objRight)
			and
			(objTop > charBottom)
			and
			(objTop-charBottom <= maxVerticalDistance)
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
		maxVerticalDistance = self.maxVerticalDistance if self.maxVerticalDistance else charRect.height
		if (
			(objLeft<=charLeft<objRight)
			and
			(charTop > objBottom)
			and
			(charTop-objBottom <= maxVerticalDistance)
		):
			distance = charTop-objBottom
			return distance


class StarExplorer:

	def __init__(self, objRect, searchDirections, maxHorizontalDistance, maxVerticalDistance):
		# obj rectangle which you look around
		self.objRect = objRect
		# max external distance from an obj point (left or right)
		self.maxHorizontalDistance = maxHorizontalDistance
		# max external distance from an obj point (top or bottom)
		self.maxVerticalDistance = maxVerticalDistance
		# methods for checking on each direction
		checkerMethods = (self.leftCheck, self.topCheck, self.rightCheck, self.bottomCheck)
		# point distances and labels collected for each direction
		self.distancesAndLabels = {}
		# checker methods to be invoke (according to passed directions)
		self.checkers = {}
		# initialize  for each passed direction
		for direction, checker in enumerate(checkerMethods):
			if direction in searchDirections:
				self.distancesAndLabels[direction] = []
				self.checkers[direction] = checker

	def getDistanceAndLabelText(self, labelObjs):
		debugLog("Labels to analyze: %d"%len(labelObjs))
		# check proximity and distance
		# for each center point around obj
		# in specified directions,
		# saving distance if compatible
		for labelObj in labelObjs:
			labelText = labelObj.name
			if not labelText or labelText.isspace():
				# TODO: manage image with OCR and AI
				continue
			centerPoint = labelObj.location.center
			for direction, checker in self.checkers.items():
				distance = checker(centerPoint)
				if distance:
					self.distancesAndLabels[direction].append((distance, labelText,))
		if not any(self.distancesAndLabels.values()):
			debugLog("No points found!")
			return
		# establish nearest label for each direction
		minDistancesAndLabels = {}
		for direction in self.checkers.keys():
			distancesAndLabels = self.distancesAndLabels[direction]
			debugLog("Distances and labels for direction %d: %s"%(direction, distancesAndLabels))
			minDistanceAndLabel = min(distancesAndLabels, key=lambda i: i[0]) if distancesAndLabels else (10000, None)
			minDistancesAndLabels[direction] = minDistanceAndLabel
		# establish the direction with nearest label
		chosenDirection = min(minDistancesAndLabels, key=minDistancesAndLabels.get)
		minDistance, labelText = minDistancesAndLabels[chosenDirection]
		if minDistance == 10000:
			debugLog("Unable to establish label position")
			return
		debugLog("Min distance: %d"%minDistance)
		return (minDistance, labelText)

	def leftCheck(self, centerPoint):
		objLeft, objTop, objRight, objBottom = self.objRect
		xPoint, yPoint = centerPoint
		if (
			(objTop<yPoint<=objBottom)
			and
			(objLeft > xPoint)
			and
			(objLeft-xPoint <= self.maxHorizontalDistance)
		):
			distance = objLeft-xPoint
			return distance

	def topCheck(self, centerPoint):
		objLeft, objTop, objRight, objBottom = self.objRect
		xPoint, yPoint = centerPoint
		if (
			(objLeft<=xPoint<objRight)
			and
			(objTop > yPoint)
			and
			(objTop-yPoint <= self.maxVerticalDistance)
		):
			distance = objTop-yPoint
			return distance

	def rightCheck(self, centerPoint):
		objLeft, objTop, objRight, objBottom = self.objRect
		xPoint, yPoint = centerPoint
		if (
			(objTop<yPoint<=objBottom)
			and
			(xPoint > objRight)
			and
			(xPoint-objRight <= self.maxHorizontalDistance)
		):
			distance = xPoint-objRight
			return distance

	def bottomCheck(self, centerPoint):
		objLeft, objTop, objRight, objBottom = self.objRect
		xPoint, yPoint = centerPoint
		if (
			(objLeft<=xPoint<objRight)
			and
			(yPoint > objBottom)
			and
			(yPoint-objBottom <= self.maxVerticalDistance)
		):
			distance = yPoint-objBottom
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

import ctypes

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
def getAllStaticHandles(parent):
	results = []
	@WNDENUMPROC
	def callback(window, data):
		isWindowVisible = winUser.isWindowVisible(window)
		isWindowEnabled = winUser.isWindowEnabled(window)
		className = winUser.getClassName(window)
		if isWindowVisible and isWindowEnabled and "static" in className.lower():
			results.append(window)
		return True
	# call previous func until it returns True,
	# thus always, getting all windows
	ctypes.windll.user32.EnumChildWindows(parent, callback, 0)
	# return all results
	return results
