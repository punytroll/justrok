#! /usr/bin/env python
## Hey, Python: encoding=utf-8
#
# Copyright (c) 2007-2010 Adeodato Simó (dato@net.com.org.es)
# Licensed under the terms of the MIT license.

import minirok

import os

from PyKDE4 import kdecore, kdeui, kio
from PyQt4 import QtCore, QtGui

import minirok
from minirok import preferences, right_side, statusbar, util

##

class MainWindow(kdeui.KXmlGuiWindow):

    CONFIG_SECTION = 'MainWindow'
    CONFIG_OPTION_SPLITTER_STATE = 'splitterState'

    def __init__ (self, *args):
        kdeui.KXmlGuiWindow.__init__(self)
        util.CallbackRegistry.register_at_exit(self.__at_exit)

        minirok.Globals.action_collection = self.actionCollection()
        minirok.Globals.preferences = preferences.Preferences()

        self.main_view = right_side.RightSide(self, main_window = self)

        self.statusbar = statusbar.StatusBar(self)
        self.setStatusBar(self.statusbar)

        self.init_systray()
        self.init_actions()

        self.setHelpMenuEnabled(False)
        self.setCentralWidget(self.main_view)
        # XXX-KDE4: I don't think this is needed anymore: check.
        # self.setAutoSaveSettings()

        setupGUI_args = [
            QtCore.QSize(900, 540),
            self.StandardWindowOption(self.ToolBar | self.Create |
                                      self.Save | self.Keys)  # Skip StatusBar.
        ]

        # If a minirokui.rc file exists in the standard location, do
        # not specify one for setupGUI(), else specify one if available.
        if kdecore.KStandardDirs.locate('appdata', 'minirokui.rc').isEmpty():
            local_rc = os.path.join(os.path.dirname(minirok.__path__[0]),
                                    'config/minirokui.rc')
            if os.path.isfile(local_rc):
                setupGUI_args.append(local_rc)

        self.setupGUI(*setupGUI_args)

        # We only want the app to exit if Quit was called from the systray icon
        # or from the File menu, not if the main window was closed. Use a flag
        # so that slot_really_quit() and queryClose() know what to do.
        self._flag_really_quit = False

    ##

    def init_actions(self):
        actionCollection = self.actionCollection()

        # File menu.
        self.action_quit = kdeui.KStandardAction.quit(self.slot_really_quit,
                                                      actionCollection)

        # Help menu.
        self.action_about = kdeui.KStandardAction.aboutApp(
            kdeui.KAboutApplicationDialog(None, self).show, actionCollection)
        self.action_about.setShortcutConfigurable(False)

        # Other.
        self.action_toggle_window = util.create_action(
            'action_toggle_window', 'Show/Hide window',
            self.systray.toggleActive, global_shortcut='Ctrl+Alt+M')

        self.action_preferences = kdeui.KStandardAction.preferences(
            self.slot_preferences, actionCollection)
        self.action_preferences.setShortcutConfigurable(False)

    def init_systray(self):
        self.systray = Systray(self)
        self.systray.connect(self.systray,
                             QtCore.SIGNAL('quitSelected()'),
                             self.slot_really_quit)
        self.systray.show()

    def slot_really_quit(self):
        self._flag_really_quit = True
        self.close()

    def slot_preferences(self):
        if kdeui.KConfigDialog.showDialog('preferences dialog'):
            return
        else:
            dialog = preferences.Dialog(self, 'preferences dialog',
                                        minirok.Globals.preferences)
            self.connect(dialog,
                         QtCore.SIGNAL('settingsChanged(const QString &)'),
                    util.CallbackRegistry.fire_apply_preferences)
            dialog.show()

    def __at_exit(self):
        pass

    ##

    def queryClose(self):
        finishing_session = kdeui.KApplication.kApplication().sessionSaving()
        if not finishing_session:
            # We want to save the shown/hidden status on session quit.
            self.hide()
        return self._flag_really_quit or finishing_session

    def queryExit(self):
        util.CallbackRegistry.fire_at_exit()
        kdecore.KGlobal.config().sync()
        return True

    def saveProperties(self, config):
        config.writeEntry('docked', bool(self.isHidden()))

    def readProperties(self, config):
        self.setShown(not config.readBoolEntry('docked', False))

##

class Systray(kdeui.KSystemTrayIcon):
    """A KSystemTrayIcon class that calls Play/Pause on middle button clicks.

    It will also show the currently played track in its tooltip.
    """
    def __init__(self, *args):
        kdeui.KSystemTrayIcon.__init__(self, *args)
        self.setIcon(self.loadIcon('minirok'))
        self.installEventFilter(self)
        self.contextMenu().addAction(minirok.Globals.action_collection.action('action_previous'))
        self.contextMenu().addAction(minirok.Globals.action_collection.action('action_play_pause'))
        self.contextMenu().addAction(minirok.Globals.action_collection.action('action_stop'))
        self.contextMenu().addAction(minirok.Globals.action_collection.action('action_next'))

        self.connect(
            self,
            QtCore.SIGNAL('activated(QSystemTrayIcon::ActivationReason)'),
            self.slot_activated)

    def slot_activated(self, reason):
        # NB: Filtering for middle button clicks in eventFilter() below does
        # not seem to work.
        if reason == QtGui.QSystemTrayIcon.MiddleClick:
            minirok.Globals.action_collection.action('action_play_pause').trigger()

    def eventFilter(self, object_, event):
        if (object_ == self
            and event.type() == QtCore.QEvent.ToolTip):
            tags = minirok.Globals.playlist.get_current_tags()
            if tags:
                title = tags.get('Title') or ''
                artist = tags.get('Artist') or ''
                if artist and title:
                    artist += ' - '
                if artist or title:
                    QtGui.QToolTip.showText(event.globalPos(), artist + title)
            return True

        return kdeui.KSystemTrayIcon.eventFilter(self, object_, event)
