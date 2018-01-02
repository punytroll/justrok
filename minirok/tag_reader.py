#! /usr/bin/env python
## Hey, Python: encoding=utf-8
#
# Copyright (c) 2007-2008, 2010 Adeodato Simó (dato@net.com.org.es)
# Licensed under the terms of the MIT license.

import minirok

import mutagen
import mutagen.easyid3
import mutagen.asf
import mutagen.id3
import mutagen.mp3

from minirok import (
    util,
)

class TagReader(util.ThreadedWorker):

    def __init__(self):
        util.ThreadedWorker.__init__(self, lambda item: self.tags(item.path))
    
    @staticmethod
    def tags(path):
        print("Reading tag for \"" + path + "\"")
        result = {}
        try:
            complex_info = mutagen.File(path)
            if isinstance(complex_info, mutagen.mp3.MP3):
                try:
                    simple_info = mutagen.easyid3.EasyID3(path)
                except mutagen.id3.ID3NoHeaderError:
                    simple_info = mutagen.easyid3.EasyID3()
            else:
                minirok.logger.warning('could not read tags from %s: mutagen.File() returned None', path)
                return result
        except Exception as exception:
            if path in str(e):  # Mutagen included the path in the exception.
                msg = 'could not read tags: %s' % e
            else:
                msg = 'could not read tags from %s: %s' % (path, e)
            minirok.logger.warning(msg)
            return result
        print("    " + str(complex_info))
        print("    " + str(simple_info))
        # Track
        if "WM/TrackNumber" in simple_info and type(simple_info["WM/TrackNumber"][0]) is mutagen.asf.ASFUnicodeAttribute:
            result["Track"] = simple_info["WM/TrackNumber"][0].value
        elif "tracknumber" in simple_info and "tracktotal" in simple_info:
            result["Track"] = simple_info["tracknumber"][0] + '/' + simple_info["tracktotal"][0]
        elif "tracknumber" in simple_info:
            result["Track"] = simple_info["tracknumber"][0]
        # Disc
        if "WM/PartOfSet" in simple_info and type(simple_info["WM/PartOfSet"][0]) is mutagen.asf.ASFUnicodeAttribute:
            result["Disc"] = simple_info["WM/PartOfSet"][0].value
        elif "discnumber" in simple_info and "disctotal" in simple_info:
            result["Disc"] = simple_info["discnumber"][0] + "/" + simple_info["disctotal"][0]
        elif "discnumber" in simple_info:
            result["Disc"] = simple_info["discnumber"][0]
        # Date
        if "WM/Year" in simple_info and type(simple_info["WM/Year"][0]) is mutagen.asf.ASFUnicodeAttribute:
            result["Date"] = simple_info["WM/Year"][0].value
        elif "date" in simple_info:
            result["Date"] = simple_info["date"][0]
        # Album
        if "WM/AlbumTitle" in simple_info and type(simple_info["WM/AlbumTitle"][0]) is mutagen.asf.ASFUnicodeAttribute:
            result["Album"] = simple_info["WM/AlbumTitle"][0].value
        elif "album" in simple_info :
            result["Album"] = simple_info["album"][0]
        # Title
        if "Title" in simple_info and type(simple_info["Title"][0]) is mutagen.asf.ASFUnicodeAttribute:
            result["Title"] = simple_info["Title"][0].value
        elif "title" in simple_info:
            result["Title"] = simple_info["title"][0]
        # Artist
        if "WM/AlbumArtist" in simple_info and type(simple_info["WM/AlbumArtist"][0]) is mutagen.asf.ASFUnicodeAttribute:
            result["Artist"] = simple_info["WM/AlbumArtist"][0].value
        elif "artist" in simple_info:
            result["Artist"] = simple_info["artist"][0]
        # Commentary
        commentary_frames = complex_info.tags.getall("COMM")
        if len(commentary_frames) > 0:
            result["Commentary"] = commentary_frames[0].text[0]
        # Length
        try:
            result['Length'] = int(complex_info.info.length)
        except AttributeError:
            pass
        print("    " + str(result))
        return result
