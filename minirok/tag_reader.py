#! /usr/bin/env python
## vim: fileencoding=utf-8
#
# Copyright (c) 2007-2008 Adeodato Simó (dato@net.com.org.es)
# Licensed under the terms of the MIT license.

import mutagen
import mutagen.id3
import mutagen.mp3
import mutagen.easyid3

import minirok
from minirok import util

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
        these may be not present in the returned dict.
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
                raise Exception, 'mutagen.File() returned None'
        except Exception, e:
            # Er, note that not only the above raise is catched here, since
            # mutagen.File() can raise exceptios as well. Wasn't obvious when I
            # revisited this code.
            if path in str(e): # mutagen normally includes the path itself
                msg = 'could not read tags: %s' % e
            else:
                msg = 'could not read tags from %s: %s' % (path, e)
            minirok.logger.warning(msg)
            return {}

        tags = {}

        for column in [ 'Track', 'Artist', 'Album', 'Title', 'Disc', 'Date' ]:
            if column == 'Track':
                tag = 'tracknumber'
            elif column == 'Disc':
                tag = 'discnumber'
            else:
                tag = column.lower()

            try:
                tags[column] = info[tag][0]
            except ValueError:
                minirok.logger.warn('invalid tag %r for %s', tag, type(info))
            except KeyError:
                # tag is not present
                pass

        try:
            tags['Length'] = int(info.info.length)
        except AttributeError:
            pass

        return tags
