#! /usr/bin/env python
## Hey, Python: encoding=utf-8
#
# Copyright (c) 2007-2008, 2010 Adeodato Simó (dato@net.com.org.es)
# Licensed under the terms of the MIT license.

import logging
import os
import re
import sys

##

filesystem_encoding = sys.getfilesystemencoding()

##

__appname__     = 'justrok'
__progname__    = 'Justrok'
__version__     = '1.0'
__description__ = 'A minimalistic music player written in Python.'
__copyright__   = 'Copyright (c) 2007-2009 Adeodato Simó, 2010-2017 Hagen Möbius'
__homepage__    = 'https://github.com/punytroll/justrok'
__bts__         = 'https://github.com/punytroll/justrok/issues'
__authors__     = [
    ('Hagen Möbius', '', 'hagen.moebius@googlemail.com'),
]
__thanksto__    = [
    # ('Name', 'Task', 'Email', 'Webpage'),
    ('Adeodato Simó',
     'For writing minirok, the basis of justrok.',
     'dato@net.com.org.es',
     ''),
    ('The Amarok developers',
     'For their design and ideas, which I copied.\n'
     'And their code, which I frequently copied in the early days.',
     '', 'http://amarok.kde.org'),
    ('Pino Toscano',
     'For saving me from KConfigDialogManager + QButtonGroup misery.',
     'pino@kde.org', ''),
]

__license__ = """\
Minirok is Copyright (c) 2007-2009 Adeodato Simó, and licensed under the
terms of the MIT license:

  Permission is hereby granted, free of charge, to any person obtaining
  a copy of this software and associated documentation files (the
  "Software"), to deal in the Software without restriction, including
  without limitation the rights to use, copy, modify, merge, publish,
  distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so, subject to
  the following conditions:

  The above copyright notice and this permission notice shall be included
  in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
  CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

##

def _minirok_logger():
    levelname = os.environ.get('MINIROK_DEBUG_LEVEL', 'warning')
    level = getattr(logging, levelname.upper(), None)

    if not isinstance(level, int):
        bogus_debug_level = True
        level = logging.WARNING
    else:
        bogus_debug_level = False

    fmt = 'minirok: %(levelname)s: %(message)s'

    stderr = logging.StreamHandler(sys.stderr)
    stderr.setFormatter(logging.Formatter(fmt))

    logger = logging.getLogger('minirok')
    logger.setLevel(level)
    logger.addHandler(stderr)

    if bogus_debug_level:
        logger.warn('invalid value for MINIROK_DEBUG_LEVEL: %r', levelname)

    return logger

logger = _minirok_logger()

del _minirok_logger

##

_do_exit = False
_not_found = []

try:
    from PyQt4 import (
        QtCore,  # This one is used below.
        QtGui,
    )
except ImportError:
    _do_exit = True
    _not_found.append('PyQt')

try:
    from PyKDE4 import (
        kdecore,
        kdeui,  # Used below.
        kio,
    )
except ImportError as e:
    _do_exit = True
    _not_found.append('PyKDE (error was: %s)' % e)

try:
    import mutagen
except ImportError:
    _do_exit = True
    _not_found.append('Mutagen')

try:
    import gi
    gi.require_version("Gst", "1.0")
    from gi.repository import Gst
except ImportError:
    _do_exit = True
    _not_found.append('GStreamer Python bindings')

try:
    import httplib2
except ImportError:
    _do_exit = True
    _not_found.append('httplib2')

try:
    import json
except ImportError:
    try:
        import simplejson
    except ImportError:
        _has_scrobble = False
    else:
        _has_scrobble = True
else:
    _has_scrobble = True

try:
    import dbus
    import dbus.mainloop.qt
except ImportError:
    _has_dbus = False
else:
    qtver = str(QtCore.qVersion())
    match = re.match(r'[\d.]+', qtver)

    if not match:
        logger.warn('could not parse Qt version: %s', qtver)
        _has_dbus = False
    else:
        version = tuple(map(int, match.group(0).split('.')))
        if version >= (4, 4, 0):
            _has_dbus = True
        else:
            logger.warn('disabling DBus interface: '
                        'Qt version is %s, but 4.4.0 is needed', qtver)
            _has_dbus = False

if _not_found:
    print('''\
The following required libraries could not be found on your system:

%s

See the "Requirements" section in the README file for details about where to
obtain these dependencies, or how to install them from your distribution.''' %
    ('\n'.join('    * %s' % s for s in _not_found)))

if _do_exit:
    sys.exit(1)

del _do_exit
del _not_found

##

class Globals(object):
    """Singleton object to hold pointers to various pieces of the program.

    See the __slots__ variable for a list of available attributes.
    """

    __slots__ = [
        'action_collection',
        'engine',
        'playlist',
        'preferences',
    ]

Globals = Globals()
