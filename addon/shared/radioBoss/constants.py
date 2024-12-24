# -*- coding: UTF-8 -*-
# RadioBOSS app module
# Copyright (C) 2024 Alberto Buffolino
# Released under GPL 2

from enum import StrEnum

class DirectValueStrEnum(StrEnum):

	def __repr__(self):
		return self.value


class Actions(DirectValueStrEnum):

	QUERY_MIC = "mic"
	PLAYBACKINFO = "playbackinfo"
	TRACKINFO = "trackinfo"

class XPaths(DirectValueStrEnum):

	PLAYBACK = ".Playback"
	CURRENT_TRACK = ".CurrentTrack/TRACK"
	POS_TRACK = ".Track/TRACK"


class TrackDetails(DirectValueStrEnum):

	ARTIST = "ARTIST"
	TITLE = "TITLE"
	ALBUM = "ALBUM"
	YEAR = "YEAR"
	GENRE = "GENRE"
	COMMENT = "COMMENT"
	FILENAME = "FILENAME"
	DURATION = "DURATION"
	PLAYCOUNT = "PLAYCOUNT"
	LASTPLAYED = "LASTPLAYED"
	INTRO = "INTRO"
	OUTRO = "OUTRO"
	LANGUAGE = "LANGUAGE"
	RATING = "RATING"
	BPM = "BPM"
	TAGS = "TAGS"
	PUBLISHER = "PUBLISHER"
	ALBUMARTIST = "ALBUMARTIST"
	COMPOSER = "COMPOSER"
	COPYRIGHT = "COPYRIGHT"
	TRACKNUMBER = "TRACKNUMBER"
	F1 = "F1"
	F2 = "F2"
	F3 = "F3"
	F4 = "F4"
	F5 = "F5"
	CASTTITLE = "CASTTITLE"
	LISTENERS = "LISTENERS"
	LYRICS = "LYRICS"
	ITEMTITLE = "ITEMTITLE"
