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
            simple_info = None
            complex_info = mutagen.File(path)
            if complex_info == None:
                minirok.logger.warning('could not read tags from %s: mutagen.File() returned None', path)
            else:
                print("Complex: " + str(complex_info))
                if isinstance(complex_info, mutagen.mp3.MP3) == True:
                    try:
                        simple_info = mutagen.easyid3.EasyID3(path)
                        print("Simple: " + str(simple_info))
                    except mutagen.id3.ID3NoHeaderError:
                        pass
                # Track
                if "WM/TrackNumber" in complex_info and type(complex_info["WM/TrackNumber"][0]) is mutagen.asf.ASFUnicodeAttribute:
                    result["Track"] = complex_info["WM/TrackNumber"][0].value
                elif simple_info != None and "tracknumber" in simple_info and "tracktotal" in simple_info:
                    result["Track"] = simple_info["tracknumber"][0] + '/' + simple_info["tracktotal"][0]
                elif "tracknumber" in complex_info and "tracktotal" in complex_info:
                    result["Track"] = complex_info["tracknumber"][0] + '/' + complex_info["tracktotal"][0]
                elif simple_info != None and "tracknumber" in simple_info:
                    result["Track"] = simple_info["tracknumber"][0]
                elif "tracknumber" in complex_info:
                    result["Track"] = complex_info["tracknumber"][0]
                # Disc
                if "WM/PartOfSet" in complex_info and type(complex_info["WM/PartOfSet"][0]) is mutagen.asf.ASFUnicodeAttribute:
                    result["Disc"] = complex_info["WM/PartOfSet"][0].value
                elif simple_info != None and "discnumber" in simple_info and "disctotal" in simple_info:
                    result["Disc"] = simple_info["discnumber"][0] + "/" + simple_info["disctotal"][0]
                elif "discnumber" in complex_info and "disctotal" in complex_info:
                    result["Disc"] = complex_info["discnumber"][0] + "/" + complex_info["disctotal"][0]
                elif simple_info != None and "discnumber" in simple_info:
                    result["Disc"] = simple_info["discnumber"][0]
                elif "discnumber" in complex_info:
                    result["Disc"] = complex_info["discnumber"][0]
                # Date
                if "WM/Year" in complex_info and type(complex_info["WM/Year"][0]) is mutagen.asf.ASFUnicodeAttribute:
                    result["Date"] = complex_info["WM/Year"][0].value
                elif simple_info != None and "date" in simple_info:
                    result["Date"] = simple_info["date"][0]
                elif "date" in complex_info:
                    result["Date"] = complex_info["date"][0]
                # Album
                if "WM/AlbumTitle" in complex_info and type(complex_info["WM/AlbumTitle"][0]) is mutagen.asf.ASFUnicodeAttribute:
                    result["Album"] = complex_info["WM/AlbumTitle"][0].value
                elif simple_info != None and "album" in simple_info :
                    result["Album"] = simple_info["album"][0]
                elif "album" in complex_info :
                    result["Album"] = complex_info["album"][0]
                # Title
                if "Title" in complex_info and type(complex_info["Title"][0]) is mutagen.asf.ASFUnicodeAttribute:
                    result["Title"] = complex_info["Title"][0].value
                elif simple_info != None and "title" in simple_info:
                    result["Title"] = simple_info["title"][0]
                elif "title" in complex_info:
                    result["Title"] = complex_info["title"][0]
                # Artist
                if "WM/AlbumArtist" in complex_info and type(complex_info["WM/AlbumArtist"][0]) is mutagen.asf.ASFUnicodeAttribute:
                    result["Artist"] = complex_info["WM/AlbumArtist"][0].value
                elif simple_info != None and "artist" in simple_info:
                    result["Artist"] = simple_info["artist"][0]
                elif "artist" in complex_info:
                    result["Artist"] = complex_info["artist"][0]
                # Commentary
                if "comment" in complex_info:
                    result["Comment"] = complex_info["comment"][0]
                elif "description" in complex_info:
                    result["Comment"] = complex_info["description"][0]
                elif isinstance(complex_info, mutagen.mp3.MP3) == True and complex_info.tags != None:
                    comment_frames = complex_info.tags.getall("COMM")
                    if len(comment_frames) > 0:
                        result["Comment"] = comment_frames[0].text[0]
                # Length
                try:
                    result['Length'] = int(complex_info.info.length)
                except AttributeError:
                    pass
        except Exception as exception:
            if path in str(exception):  # Mutagen included the path in the exception.
                msg = 'could not read tags: %s' % exception
            else:
                msg = 'could not read tags from %s: %s' % (path, exception)
            minirok.logger.warning(msg)
        print("Result: " + str(result))
        print
        return result
