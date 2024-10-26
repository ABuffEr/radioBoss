# -*- coding: UTF-8 -*-
# RadioBOSS app module
# Copyright (C) 2024 Alberto Buffolino
# Released under GPL 2

import base64
import time

def encodeBase64String(strIn):
	base64Bytes = base64.b64encode(strIn.encode("UTF-8"))
	strOut = base64Bytes.decode("UTF-8")
	return strOut

def decodeBase64String(strIn):
	strBytes = base64.b64decode(strIn)
	strOut = strBytes.decode("UTF-8")
	return strOut

def fixedTime(millis):
	seconds = int(millis)/1000
	res = time.strftime("%M:%S", time.gmtime(seconds))
	return res
