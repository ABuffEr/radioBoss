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

DEBUG = False
TEMPLATE = "{protocol}://{host}:{port}/?pass={pwd}&action={action}"

def debugLog(message):
	if DEBUG:
		log.info(message)

def errMsg(info):
	msg = _("Something went wrong.\nAPI response: {data}")
	return msg.format(data=info)

def buildURL(action, params=None):
	protocol = addonConfig["protocol"]
	host = addonConfig["host"]
	port = addonConfig["port"]
	encodedPwd = addonConfig["password"]
	pwd = utils.decodeBase64String(encodedPwd)
	url = TEMPLATE.format(protocol=protocol, host=host, port=port, pwd=pwd, action=action)
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
	status = asyncio.run(fetchURL(action="mic"))
	if status == "0":
		msg = _("Mic off")
		return msg
	elif status == "1":
		msg = _("Mic on")
		return msg
	else:
		return errMsg(status)

def getSongElapsedTime():
	msg = _("Elapsed time: {time}")
	info = asyncio.run(fetchURL(action="playbackinfo"))
	try:
		pos = xmlParser.parse(info, ".Playback", "pos")
		fixedPos = utils.fixedTime(pos)
		return msg.format(time=fixedPos)
	except:
		return errMsg(info)

def getSongRemainingTime():
	msg = _("Remaining time: {time}")
	info = asyncio.run(fetchURL(action="playbackinfo"))
	try:
		parsedAttrs = xmlParser.parse(info, ".Playback", ("pos", "len",))
		pos, length = parsedAttrs.values()
		remTime = int(length)-int(pos)
		fixedRemTime = utils.fixedTime(remTime)
		return msg.format(time=fixedRemTime)
	except:
		return errMsg(info)


class Fetcher(Thread):

	def __init__(self, url, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.url = url
		self.res = None

	def run(self):
		req = requests.get(self.url)
		self.res = req.text
