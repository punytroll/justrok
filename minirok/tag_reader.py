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
        try:
            info = mutagen.File(path)
            if isinstance(info, mutagen.mp3.MP3):
                # We really want an EasyID3 object, so we re-read the tags now.
                # Alas, EasyID3 does not include the .info part, which contains
                # the length, so we save it from the MP3 object.
                dot_info = info.info
                try:
                    info = mutagen.easyid3.EasyID3(path)
                except mutagen.id3.ID3NoHeaderError:
                    info = mutagen.easyid3.EasyID3()
                info.info = dot_info
            elif info is None:
                minirok.logger.warning(
                    'could not read tags from %s: mutagen.File() returned None',
                    path)
                return {}
        except Exception as e:
            if path in str(e):  # Mutagen included the path in the exception.
                msg = 'could not read tags: %s' % e
            else:
                msg = 'could not read tags from %s: %s' % (path, e)
            minirok.logger.warning(msg)
            return {}
        print(info)
        result = {}
        # Track
        if "WM/TrackNumber" in info and type(info["WM/TrackNumber"][0]) is mutagen.asf.ASFUnicodeAttribute:
            result["Track"] = info["WM/TrackNumber"][0].value
        elif "tracknumber" in info and "tracktotal" in info:
            result["Track"] = info["tracknumber"][0] + '/' + info["tracktotal"][0]
        elif "tracknumber" in info:
            result["Track"] = info["tracknumber"][0]
        # Disc
        if "WM/PartOfSet" in info and type(info["WM/PartOfSet"][0]) is mutagen.asf.ASFUnicodeAttribute:
            result["Disc"] = info["WM/PartOfSet"][0].value
        elif "discnumber" in info and "disctotal" in info:
            result["Disc"] = info["discnumber"][0] + "/" + info["disctotal"][0]
        elif "discnumber" in info:
            result["Disc"] = info["discnumber"][0]
        # Date
        if "WM/Year" in info and type(info["WM/Year"][0]) is mutagen.asf.ASFUnicodeAttribute:
            result["Date"] = info["WM/Year"][0].value
        elif "date" in info:
            result["Date"] = info["date"][0]
        # Album
        if "WM/AlbumTitle" in info and type(info["WM/AlbumTitle"][0]) is mutagen.asf.ASFUnicodeAttribute:
            result["Album"] = info["WM/AlbumTitle"][0].value
        elif "album" in info :
            result["Album"] = info["album"][0]
        # Title
        if "Title" in info and type(info["Title"][0]) is mutagen.asf.ASFUnicodeAttribute:
            result["Title"] = info["Title"][0].value
        elif "title" in info:
            result["Title"] = info["title"][0]
        # Artist
        if "WM/AlbumArtist" in info and type(info["WM/AlbumArtist"][0]) is mutagen.asf.ASFUnicodeAttribute:
            result["Artist"] = info["WM/AlbumArtist"][0].value
        elif "artist" in info:
            result["Artist"] = info["artist"][0]
        # Length
        try:
            result['Length'] = int(info.info.length)
        except AttributeError:
            pass
        
        return result
