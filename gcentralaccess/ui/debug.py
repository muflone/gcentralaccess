##
#     Project: gCentralAccess
# Description: Manage external resources from a centralized management console
#      Author: Fabio Castelli (Muflone) <muflone@vbsimple.net>
#   Copyright: 2015-2016 Fabio Castelli
#     License: GPL-2+
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
##

import datetime

from gi.repository import Gtk

import gcentralaccess.preferences as preferences
from gcentralaccess.preferences import (
    DEBUG_ENABLED, DEBUG_ENABLED_HIDDEN, DEBUG_SHOW_INFO, DEBUG_SHOW_WARNING,
    DEBUG_SHOW_ERROR, DEBUG_TIMESTAMP, DEBUG_FOLLOW_TEXT)
import gcentralaccess.settings as settings
from gcentralaccess.functions import get_ui_file, text, process_events
from gcentralaccess.gtkbuilder_loader import GtkBuilderLoader

SECTION_WINDOW_NAME = 'debug'

DEBUG_FORMAT_TIMESTAMP = '[{:%Y-%m-%d %H:%M:%S}]'
DEBUG_FORMAT = '{timestamp} {severity}: {text}\n'
INFO = 'INFO'
WARNING = 'WARNING'
ERROR = 'ERROR'

debug = None


class UIDebug(object):
    def __init__(self, parent, delete_event_cb):
        """Prepare the Debug dialog"""
        self.on_window_debug_delete_event = delete_event_cb
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('debug.glade'))
        # Initialize preferences
        self.actions_preferences = {
            DEBUG_ENABLED: self.ui.action_enable,
            DEBUG_ENABLED_HIDDEN: self.ui.action_enable_hidden,
            DEBUG_SHOW_INFO: self.ui.action_show_info,
            DEBUG_SHOW_WARNING: self.ui.action_show_warning,
            DEBUG_SHOW_ERROR: self.ui.action_show_error,
            DEBUG_TIMESTAMP: self.ui.action_show_timestamp,
            DEBUG_FOLLOW_TEXT: self.ui.action_follow_text,
        }
        for key in self.actions_preferences:
            self.actions_preferences[key].set_active(preferences.get(key))
        # Initialize actions
        for widget in self.ui.get_objects_by_type(Gtk.Action):
            # Connect the actions accelerators
            widget.connect_accelerator()
            # Set labels
            widget.set_label(text(widget.get_label()))
        # Initialize tooltips
        for widget in self.ui.get_objects_by_type(Gtk.ToolButton):
            action = widget.get_related_action()
            if action:
                widget.set_tooltip_text(action.get_label().replace('_', ''))
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def show(self):
        """Show the Debug dialog"""
        settings.positions.restore_window_position(
            self.ui.window_debug, SECTION_WINDOW_NAME)
        self.ui.window_debug.show()

    def hide(self):
        """Hide the Debug dialog"""
        settings.positions.save_window_position(
            self.ui.window_debug, SECTION_WINDOW_NAME)
        self.ui.window_debug.hide()

    def destroy(self):
        """Destroy the Debug dialog"""
        self.hide()
        self.ui.window_debug.destroy()
        self.ui.window_debug = None

    def clear(self):
        """Clear the debug buffer"""
        self.ui.buffer_debug.set_text('')

    def add_text(self, text):
        """Add a text to the debug buffer"""
        if preferences.get(DEBUG_ENABLED) and (
                preferences.get(DEBUG_ENABLED_HIDDEN) or
                self.ui.window_debug.get_visible()):
            # Insert the text at the end
            self.ui.buffer_debug.insert(self.ui.buffer_debug.get_end_iter(),
                                        text)
            # Follow the text if requested
            if preferences.get(DEBUG_FOLLOW_TEXT):
                process_events()
                self.ui.textview_debug.scroll_to_iter(
                    iter=self.ui.buffer_debug.get_end_iter(),
                    within_margin=0.0,
                    use_align=False,
                    xalign=0.0,
                    yalign=0.0)

    def add_line(self, severity, text):
        """Add a text line to the debug buffer"""
        # Check the requested severity level
        if (severity == INFO and preferences.get(DEBUG_SHOW_INFO) or
            (severity == WARNING and preferences.get(DEBUG_SHOW_WARNING)) or
                (severity == ERROR and preferences.get(DEBUG_SHOW_ERROR))):
            timestamp = (DEBUG_FORMAT_TIMESTAMP.format(datetime.datetime.now())
                         if preferences.get(DEBUG_TIMESTAMP) else '')
            self.add_text(DEBUG_FORMAT.format(timestamp=timestamp,
                                              severity=severity,
                                              text=text))

    def add_info(self, text):
        """Add a text line to the debug buffer with severity info"""
        self.add_line(INFO, text)

    def add_warning(self, text):
        """Add a text line to the debug buffer with severity warning"""
        self.add_line(WARNING, text)

    def add_error(self, text):
        """Add a text line to the debug buffer with severity error"""
        self.add_line(ERROR, text)

    def on_action_clear_activate(self, action):
        """Clear the debug text"""
        self.clear()

    def on_action_set_debug_flag(self, action):
        """Enable/disable various debug flags"""
        for key in self.actions_preferences:
            if action is self.actions_preferences[key]:
                preferences.set(key, action.get_active())
                break


def add_text(text):
    """Add a text to the debug buffer"""
    if debug:
        debug.add_text(text)


def add_line(severity, text):
    """Add a text line to the debug buffer"""
    if debug:
        debug.add_line(severity, text)


def add_info(text):
    """Add a text line to the debug buffer with severity info"""
    if debug:
        debug.add_info(text)


def add_warning(text):
    """Add a text line to the debug buffer with severity warning"""
    if debug:
        debug.add_warning(text)


def add_error(text):
    """Add a text line to the debug buffer with severity error"""
    if debug:
        debug.add_error(text)
