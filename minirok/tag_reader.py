#! /usr/bin/env python
## Hey, Python: encoding=utf-8
#
# Copyright (c) 2007-2008, 2010 Adeodato Simó (dato@net.com.org.es)
# Licensed under the terms of the MIT license.

import minirok

import mutagen
import mutagen.easyid3
import mutagen.id3
import mutagen.mp3

from minirok import (
    util,
)

##

class TagReader(util.ThreadedWorker):
    """Worker to read tags from files."""

    def __init__(self):
        util.ThreadedWorker.__init__(self, lambda item: self.tags(item.path))

    ##

    @staticmethod
    def tags(path):
        """Return a dict with the tags read from the given path.

        Tags that will be read: Track, Artist, Album, Title, Length. Any of
        these may be missing in the returned dict.
        """
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
        for column in [ 'Track', 'Artist', 'Album', 'Title', 'Disc', 'Date' ]:
            try:
                if column == 'Track':
                    if 'tracktotal' in info:
                        result[column] = info['tracknumber'][0] + '/' + info['tracktotal'][0]
                    else:
                        result[column] = info['tracknumber'][0]
                elif column == 'Disc':
                    if 'disctotal' in info:
                        result[column] = info['discnumber'][0] + '/' + info['disctotal'][0]
                    else:
                        result[column] = info['discnumber'][0]
                else:
                    result[column] = info[column.lower()][0]
            except ValueError:
                minirok.logger.warn('invalid tag %r for %s', tag, type(info))
            except KeyError:
                pass  # Tag is not present in the file.
        try:
            result['Length'] = int(info.info.length)
        except AttributeError:
            pass

        return result
