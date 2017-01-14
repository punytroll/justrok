#! /usr/bin/env python
## Hey, Python: encoding=utf-8
#
# Copyright (c) 2007-2008, 2010 Adeodato Simó (dato@net.com.org.es)
# Licensed under the terms of the MIT license.

import minirok

import os
import urllib

import gi
gi.require_version("Gst", "1.0")
from gi.repository import GObject, Gst

from PyQt4 import QtCore

GObject.threads_init()
Gst.init(None)

##

class State:
    """This class holds the possible values for engine status."""
    PLAYING = object()
    STOPPED = object()
    PAUSED  = object()

##

class GStreamerEngine(QtCore.QObject):
    SINK = 'alsasink'

    PLUGINS = {
        'faad': ['.m4a'],
        'flac': [ '.flac' ],
        'mad': [ '.mp3', '.mp2', '.mp1', '.mpga' ],
        'libav': [ '.aac', '.mpc', '.mp+', '.amr', '.wma' ],
        'vorbis': [ '.ogg' ],
        'wavpack': [ '.wv', '.wvp' ]
    }

    def __init__(self):
        QtCore.QObject.__init__(self)

        self._supported_extensions = [ ".wav" ]
        for plugin, extensions in self.PLUGINS.items():
            print("Testing plugin \"" + plugin + "\" ...")
            if Gst.Registry.find_plugin(Gst.Registry.get(), plugin) is not None:
                print("supported.")
                self._supported_extensions.extend(extensions)
            else:
                print("NOT supported.")

        self.uri = None
        self._status = State.STOPPED
        self.bin = Gst.ElementFactory.make('playbin', None)
        self.bin.set_property('video-sink', None)
        try:
            device = Gst.parse_launch(self.SINK)
        except GObject.GError:
            pass
        else:
            self.bin.set_property('audio-sink', device)

        bus = self.bin.get_bus()
        bus.add_signal_watch()
        bus.connect('message::eos', self._message_eos)
        bus.connect('message::error', self._message_error)
        bus.connect('message::async-done', self._message_async_done)

        self.time_fmt = Gst.Format(Gst.Format.TIME)
        self.seek_pending = False

    ##

    def _set_status(self, value):
        if value != self._status:
            self._status = value
            self.emit(QtCore.SIGNAL('status_changed'), value)

    status = property(lambda self: self._status, _set_status)

    ##

    def can_play_path(self, path):
        """Return True if the engine can play the given file.

        This is done by looking at the extension of the file.
        """
        prefix, extension = os.path.splitext(path)
        return extension.lower() in self._supported_extensions

    ##

    def play(self, path):
        self.bin.set_state(Gst.State.NULL)
        self.uri = 'file://' + urllib.quote(os.path.abspath(path), ' /')
        self.bin.set_property('uri', self.uri)
        self.bin.set_state(Gst.State.PLAYING)
        self.status = State.PLAYING

    def pause(self, paused=True):
        if paused:
            self.bin.set_state(Gst.State.PAUSED)
            self.status = State.PAUSED
        else:
            self.bin.set_state(Gst.State.PLAYING)
            self.status = State.PLAYING

    def stop(self):
        self.bin.set_state(Gst.State.NULL)
        self.status = State.STOPPED

    def get_position(self):
        """Returns the current position as an int in seconds."""
        try:
            return int(round(self.bin.query_position(self.time_fmt)[1] / Gst.SECOND))
        except Gst.QueryError:
            return 0

    def set_position(self, seconds):
        """Seek to the given position in the current track.

        This method does not block; "seek_finished" will be emitted
        after the seek has been performed.
        """
        self.seek_pending = True
        self.bin.seek_simple(self.time_fmt, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, seconds * Gst.SECOND)

    ##

    def _message_eos(self, bus, message):
        self.bin.set_state(Gst.State.NULL)
        self.status = State.STOPPED
        self.emit(QtCore.SIGNAL('end_of_stream'))

    def _message_error(self, bus, message):
        error, debug_info = message.parse_error()
        minirok.logger.warning('engine error: %s (%s)', error, self.uri)
        self._message_eos(bus, message)

    def _message_async_done(self, bus, message):
        if self.seek_pending:
            self.seek_pending = False
            self.emit(QtCore.SIGNAL('seek_finished'))

##

Engine = GStreamerEngine
