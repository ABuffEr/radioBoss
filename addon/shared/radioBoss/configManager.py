# -*- coding: UTF-8 -*-
# RadioBOSS app module
# Copyright (C) 2024 Alberto Buffolino
# Released under GPL 2

import addonHandler
import config

confspec = {
	"protocol": "string(default=http)",
	"host": "string(default=127.0.0.1)",
	"port": "integer(default=9000)",
	"password": "string(default='')",
}
addonName = addonHandler.getCodeAddon().manifest["name"]
config.conf.spec[addonName] = confspec

addonConfig = config.conf[addonName]
