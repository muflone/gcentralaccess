##
#     Project: gCentralAccess
# Description: Manage external resources from a centralized management console
#      Author: Fabio Castelli (Muflone) <muflone@vbsimple.net>
#   Copyright: 2015 Fabio Castelli
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

from .constants import FILE_UI_MAIN
from .functions import show_dialog_fileopen, _
from .settings import *
from .gtkbuilder_loader import GtkBuilderLoader
from .ui_about import UIAbout
from gi.repository import Gtk
from gi.repository import Gdk


class UIMain(object):
    def __init__(self, application, settings):
        self.application = application
        self.settings = settings
        self.loadUI()
        self.about = UIAbout(self.ui.win_main, settings, False)
        # Restore the saved size and position
        if self.settings.get_setting(SETTING_MAIN_WINDOW_WIDTH) and \
                self.settings.get_setting(SETTING_MAIN_WINDOW_HEIGHT):
            self.ui.win_main.set_default_size(
                self.settings.get_setting(SETTING_MAIN_WINDOW_WIDTH, -1),
                self.settings.get_setting(SETTING_MAIN_WINDOW_HEIGHT, -1))
        if self.settings.get_setting(SETTING_MAIN_WINDOW_LEFT) and \
                self.settings.get_setting(SETTING_MAIN_WINDOW_TOP):
            self.ui.win_main.move(
                self.settings.get_setting(SETTING_MAIN_WINDOW_LEFT),
                self.settings.get_setting(SETTING_MAIN_WINDOW_TOP))

    def loadUI(self):
        """Load the interface UI"""
        self.ui = GtkBuilderLoader(FILE_UI_MAIN)
        self.ui.win_main.set_application(self.application)
        # Set the actions accelerator group
        for group_name in ('actions_application', ):
            for action in self.ui.get_object(group_name).list_actions():
                action.set_accel_group(self.ui.accelerators)
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def run(self):
        """Show the UI"""
        self.ui.win_main.show_all()

    def on_win_main_delete_event(self, widget, event):
        """Save the settings and close the application"""
        # Window position
        position = self.ui.win_main.get_position()
        self.settings.set_setting(SETTING_MAIN_WINDOW_LEFT, position[0])
        self.settings.set_setting(SETTING_MAIN_WINDOW_TOP, position[1])
        # Window size
        size = self.ui.win_main.get_size()
        self.settings.set_setting(SETTING_MAIN_WINDOW_WIDTH, size[0])
        self.settings.set_setting(SETTING_MAIN_WINDOW_HEIGHT, size[1])
        # Save settings and quit
        self.settings.save()
        self.about.destroy()
        self.application.quit()

    def on_action_application_about_activate(self, action):
        """Show the about dialog"""
        self.about.show()

    def on_action_application_quit_activate(self, action):
        """Close the application by closing the main window"""
        event = Gdk.Event()
        event.key.type = Gdk.EventType.DELETE
        self.ui.win_main.event(event)
