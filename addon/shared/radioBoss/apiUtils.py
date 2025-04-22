# -*- coding: UTF-8 -*-
# RadioBOSS app module
# Copyright (C) 2024 Alberto Buffolino
# Released under GPL 2

import asyncio
import requests

from logHandler import log
from threading import Thread

from . import utils, xmlParser
from .configManager import addonConfig
from .constants import Actions, XPaths, TrackDetails

DEBUG = False
TEMPLATE = "{protocol}://{host}:{port}/?pass={pwd}&action={action}"

def debugLog(message):
	if DEBUG:
		log.info(message)

def errMsg(info):
	msg = _("Something went wrong. See log for details")
	log.error("RadioBOSS API response: {data}".format(data=info))
	return msg

def buildURL(action, params=None):
	protocol = addonConfig["protocol"]
	host = addonConfig["host"]
	port = addonConfig["port"]
	encodedPwd = addonConfig["password"]
	pwd = utils.decodeBase64String(encodedPwd)
	url = TEMPLATE.format(protocol=protocol, host=host, port=port, pwd=pwd, action=action)
	if params:
		url = '&'.join([url, *params])
	return url

async def fetchURL(**kwargs):
	url = buildURL(**kwargs)
	debugLog("Fetching URL: %s"%url)
	fetcher = Fetcher(url)
	fetcher.start()
	while fetcher.is_alive():
		await asyncio.sleep(0.1)
	fetcher.join()
	res = fetcher.res
	return res

# API calls

def getMicStatus():
	status = asyncio.run(fetchURL(action=Actions.QUERY_MIC))
	if status == "0":
		msg = _("Mic off")
	elif status == "1":
		msg = _("Mic on")
	else:
		msg = errMsg(status)
	return msg

def getSongElapsedTime():
	msg = _("Track elapsed time: {time}")
	info = asyncio.run(fetchURL(action=Actions.PLAYBACKINFO))
	try:
		pos = xmlParser.parse(info, XPaths.PLAYBACK, "pos")
		fixedPos = utils.fixedTime(pos)
		return msg.format(time=fixedPos)
	except Exception as e:
		debugLog(e)
		return errMsg(info)

def getSongRemainingTime():
	msg = _("Track remaining time: {time}")
	info = asyncio.run(fetchURL(action=Actions.PLAYBACKINFO))
	try:
		parsedAttrs = xmlParser.parse(info, XPaths.PLAYBACK, ("pos", "len",))
		pos, length = parsedAttrs.values()
		remTime = int(length)-int(pos)
		fixedRemTime = utils.fixedTime(remTime)
		return msg.format(time=fixedRemTime)
	except Exception as e:
		debugLog(e)
		return errMsg(info)

def getPlaylistRemainingTime():
	msg = _("Playlist remaining time: {time}")
	info = asyncio.run(fetchURL(action=Actions.PLAYBACKINFO))
	try:
		remTime = xmlParser.parse(info, XPaths.PLAYBACK, "playingtimeleft")
		fixedRemTime = utils.fixedTime(remTime)
		return msg.format(time=fixedRemTime)
	except Exception as e:
		debugLog(e)
		return errMsg(info)

def getCurrentTrackInfo(detail):
	msg = _("{detail} of the current track: {res}")
	info = asyncio.run(fetchURL(action=Actions.PLAYBACKINFO))
	try:
		res = xmlParser.parse(info, XPaths.CURRENT_TRACK, detail)
		return msg.format(detail=detail.title(), res=res)
	except Exception as e:
		debugLog(e)
		return errMsg(info)

def getPlaybackTrackInfo(track, details=None):
	info = asyncio.run(fetchURL(action=Actions.PLAYBACKINFO))
	XPath = getattr(XPaths, "%s_TRACK"%track.upper())
	details = tuple(TrackDetails) if not details else tuple(details)
	try:
		res = xmlParser.parse(info, XPath, details)
		return res
	except Exception as e:
		debugLog(e)
		return errMsg(info)

def getPosTrackInfo(pos, detail):
	msg = _("{detail} of track {pos}: {res}")
	params = ("pos=%d"%pos,)
	info = asyncio.run(fetchURL(action=Actions.TRACKINFO, params=params))
	try:
		res = xmlParser.parse(info, XPaths.POS_TRACK, detail)
		return msg.format(detail=detail.title(), pos=pos, res=res)
	except Exception as e:
		debugLog(e)
		return errMsg(info)

def getFullPosTrackInfo(pos):
	params = ("pos=%d"%pos,)
	details = tuple(TrackDetails)
	info = asyncio.run(fetchURL(action=Actions.TRACKINFO, params=params))
	try:
		res = xmlParser.parse(info, XPaths.POS_TRACK, details)
		return res
	except Exception as e:
		debugLog(e)
		return errMsg(info)


class Fetcher(Thread):

	def __init__(self, url, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.url = url
		self.res = None

	def run(self):
		req = requests.get(self.url)
		self.res = req.text
