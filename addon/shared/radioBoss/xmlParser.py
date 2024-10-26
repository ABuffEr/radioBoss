# -*- coding: UTF-8 -*-
# RadioBOSS app module
# Copyright (C) 2024 Alberto Buffolino
# Released under GPL 2

from xml.etree import ElementTree
from multipledispatch import dispatch

@dispatch(str, str)
def parse(info, tag) -> dict[str, str]:
	parsedInfo = ElementTree.fromstring(info)
	parsedTag = parsedInfo.find(tag)
	res = parsedTag.attrib
	return res

@dispatch(str, str, str)
def parse(info, tag, attr) -> str:
	parsedTag = parse(info, tag)
	res = parsedTag.get(attr)
	return res

@dispatch(str, str, tuple)
def parse(info, tag, attrs) -> dict[str, str]:
	parsedTag = parse(info, tag)
	res = {}
	for attr in attrs:
		res[attr] = parsedTag.get(attr)
	return res
