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

from gcentralaccess.constants import (
    APP_NAME,
    FILE_SETTINGS, FILE_WINDOWS_POSITION, FILE_SERVICES)
from gcentralaccess.functions import get_ui_file, _
from gcentralaccess.preferences import Preferences
from gcentralaccess.settings import Settings
from gcentralaccess.gtkbuilder_loader import GtkBuilderLoader
from .about import UIAbout
from .services import UIServices
from gcentralaccess.service_info import ServiceInfo
from gi.repository import Gtk
from gi.repository import Gdk

SECTION_WINDOW_NAME = 'main'
SECTION_SERVICE_DESCRIPTION = 'description'
SECTION_SERVICE_COMMAND = 'command'
SECTION_SERVICE_TERMINAL = 'terminal'
SECTION_SERVICE_ICON = 'icon'


class UIMain(object):
    def __init__(self, application):
        self.application = application
        self.services = {}
        # Load settings
        self.settings = Settings(FILE_SETTINGS)
        self.settings_positions = Settings(FILE_WINDOWS_POSITION)
        self.preferences = Preferences(self.settings)
        self.settings_services = Settings(FILE_SERVICES)
        # Load services
        for key in self.settings_services.get_sections():
            self.services[key] = ServiceInfo(
                name=key,
                description=self.settings_services.get(
                    key, SECTION_SERVICE_DESCRIPTION),
                command=self.settings_services.get(
                    key, SECTION_SERVICE_COMMAND),
                terminal=self.settings_services.get_boolean(
                    key, SECTION_SERVICE_TERMINAL),
                icon=self.settings_services.get(
                    key, SECTION_SERVICE_ICON))
        self.loadUI()
        self.about = UIAbout(self.ui.win_main, False)
        # Restore the saved size and position
        self.settings_positions.restore_window_position(
            self.ui.win_main, SECTION_WINDOW_NAME)

    def loadUI(self):
        """Load the interface UI"""
        self.ui = GtkBuilderLoader(get_ui_file('main.glade'))
        self.ui.win_main.set_application(self.application)
        self.ui.win_main.set_title(APP_NAME)
        # Connect the actions accelerators
        for group_name in ('actions_application', ):
            for action in self.ui.get_object(group_name).list_actions():
                action.connect_accelerator()
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def run(self):
        """Show the UI"""
        self.ui.win_main.show_all()

    def on_win_main_delete_event(self, widget, event):
        """Save the settings and close the application"""
        self.settings_positions.save_window_position(
            self.ui.win_main, SECTION_WINDOW_NAME)
        self.settings_positions.save()
        self.settings_services.save()
        self.settings.save()
        self.about.destroy()
        self.application.quit()

    def on_action_about_activate(self, action):
        """Show the about dialog"""
        self.about.show()

    def on_action_quit_activate(self, action):
        """Close the application by closing the main window"""
        event = Gdk.Event()
        event.key.type = Gdk.EventType.DELETE
        self.ui.win_main.event(event)

    def on_action_services_activate(self, action):
        """Edit services"""
        dialog_services = UIServices(
            parent=self.ui.win_main,
            preferences=self.preferences,
            settings_positions=self.settings_positions)
        # Load services list
        dialog_services.model.load(self.services)
        dialog_services.show()
        # Get the new services list, clear and store the list again
        self.services = dialog_services.model.dump()
        dialog_services.destroy()
        self.settings_services.clear()
        for key in self.services.iterkeys():
            self.settings_services.set(
                section=key,
                option=SECTION_SERVICE_DESCRIPTION,
                value=self.services[key].description)
            self.settings_services.set(
                section=key,
                option=SECTION_SERVICE_COMMAND,
                value=self.services[key].command)
            self.settings_services.set_boolean(
                section=key,
                option=SECTION_SERVICE_TERMINAL,
                value=self.services[key].terminal)
            self.settings_services.set(
                section=key,
                option=SECTION_SERVICE_ICON,
                value=self.services[key].icon)
