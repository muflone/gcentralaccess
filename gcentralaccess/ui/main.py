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

import os
import os.path

from gi.repository import Gtk
from gi.repository import Gdk

from gcentralaccess.constants import (
    APP_NAME,
    FILE_SETTINGS, FILE_WINDOWS_POSITION, FILE_SERVICES, DIR_HOSTS)
from gcentralaccess.functions import get_ui_file, _
from gcentralaccess.preferences import Preferences
from gcentralaccess.settings import Settings
from gcentralaccess.gtkbuilder_loader import GtkBuilderLoader

from gcentralaccess.models.service_info import ServiceInfo
from gcentralaccess.models.host_info import HostInfo
from gcentralaccess.models.hosts import ModelHosts
from gcentralaccess.models.destination_info import DestinationInfo

from gcentralaccess.ui.about import UIAbout
from gcentralaccess.ui.services import UIServices
from gcentralaccess.ui.host import UIHost
from gcentralaccess.ui.message_dialog import (
    show_message_dialog, UIMessageDialogNoYes)

SECTION_WINDOW_NAME = 'main'
SECTION_SERVICE_DESCRIPTION = 'description'
SECTION_SERVICE_COMMAND = 'command'
SECTION_SERVICE_TERMINAL = 'terminal'
SECTION_SERVICE_ICON = 'icon'
SECTION_HOST = 'host'
SECTION_HOST_NAME = 'name'
SECTION_HOST_DESCRIPTION = 'description'
SECTION_DESTINATIONS = 'destinations'


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
        self.model = ModelHosts(self.ui.store_hosts, self.preferences)
        # Load hosts
        for filename in os.listdir(DIR_HOSTS):
            settings_host = Settings(os.path.join(DIR_HOSTS, filename))
            name = settings_host.get(SECTION_HOST, SECTION_HOST_NAME)
            description = settings_host.get(SECTION_HOST,
                                            SECTION_HOST_DESCRIPTION)
            self.model.add_data(HostInfo(name=name, description=description))
            # Load host destinations
            if SECTION_DESTINATIONS in settings_host.get_sections():
                for option in settings_host.get_options(SECTION_DESTINATIONS):
                    values = settings_host.get(SECTION_DESTINATIONS, option)
                    type, value = values.split(':', 1)
                    self.model.add_destination(name,
                                               DestinationInfo(option,
                                                               value,
                                                               type))
        # Restore the saved size and position
        self.settings_positions.restore_window_position(
            self.ui.win_main, SECTION_WINDOW_NAME)

    def loadUI(self):
        """Load the interface UI"""
        self.ui = GtkBuilderLoader(get_ui_file('main.glade'))
        self.ui.win_main.set_application(self.application)
        self.ui.win_main.set_title(APP_NAME)
        # Initialize actions
        for widget in self.ui.get_objects_by_type(Gtk.Action):
            # Connect the actions accelerators
            widget.connect_accelerator()
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
        self.application.quit()

    def on_action_about_activate(self, action):
        """Show the about dialog"""
        dialog = UIAbout(self.ui.win_main)
        dialog.show()
        dialog.destroy()

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

    def on_action_new_activate(self, action):
        """Define a new host"""
        dialog = UIHost(
            parent=self.ui.win_main,
            hosts=self.model,
            preferences=self.preferences,
            settings_positions=self.settings_positions)
        response = dialog.show(default_name='',
                               default_description='',
                               title=_('Add a new host'),
                               treeiter=None)
        if response == Gtk.ResponseType.OK:
            # Save host settings
            settings_host = Settings(
                os.path.join(DIR_HOSTS, '%s.conf' % dialog.name))
            settings_host.set(SECTION_HOST, SECTION_HOST_NAME, dialog.name)
            settings_host.set(SECTION_HOST, SECTION_HOST_DESCRIPTION,
                              dialog.description)
            self.model.add_data(HostInfo(name=dialog.name,
                                         description=dialog.description))
            # Save host destinations
            destinations = dialog.destinations.dump()
            for key in destinations:
                destination = destinations[key]
                self.model.add_destination(dialog.name, destination)
                settings_host.set(
                    SECTION_DESTINATIONS, destination.name,
                    '%s:%s' % (destination.type, destination.value))
            settings_host.save()
        dialog.destroy()

    def on_action_edit_activate(self, action):
        """Define a new host"""
        selection = self.ui.tvw_connections.get_selection().get_selected()
        selected_row = selection[1]
        if selected_row:
            name = self.model.get_key(selected_row)
            description = self.model.get_description(selected_row)
            selected_iter = self.model.get_iter(name)
            dialog = UIHost(
                parent=self.ui.win_main,
                hosts=self.model,
                preferences=self.preferences,
                settings_positions=self.settings_positions)
            # Restore the destinations for the selected host
            destinations = self.model.get_destinations(name)
            for key in destinations:
                dialog.destinations.add_data(destinations[key])
            # Show the edit host dialog
            response = dialog.show(default_name=name,
                                   default_description=description,
                                   title=_('Edit host'),
                                   treeiter=selected_iter)
            if response == Gtk.ResponseType.OK:
                # Create a new setting file
                new_filename = os.path.join(DIR_HOSTS, '%s.conf' % dialog.name)
                tmp_filename = os.path.join('%s.tmp' % new_filename)
                if os.path.isfile(tmp_filename):
                    os.unlink(tmp_filename)
                # Save host settings
                settings_host = Settings(tmp_filename)
                settings_host.set(SECTION_HOST, SECTION_HOST_NAME, dialog.name)
                settings_host.set(SECTION_HOST, SECTION_HOST_DESCRIPTION,
                                  dialog.description)
                self.model.add_data(HostInfo(name=dialog.name,
                                             description=dialog.description))
                # Save host destinations
                self.model.clear_destinations(dialog.name)
                destinations = dialog.destinations.dump()
                for key in destinations:
                    destination = destinations[key]
                    self.model.add_destination(dialog.name, destination)
                    settings_host.set(
                        SECTION_DESTINATIONS, destination.name,
                        '%s:%s' % (destination.type, destination.value))
                settings_host.save()
                # Save the changes to files
                old_filename = os.path.join('%s.old' % new_filename)
                try:
                    if os.path.isfile(new_filename):
                        os.rename(new_filename, old_filename)
                    os.rename(tmp_filename, new_filename)
                    if os.path.isfile(old_filename):
                        os.unlink(old_filename)
                finally:
                    if os.path.isfile(tmp_filename):
                        os.unlink(tmp_filename)
            dialog.destroy()

    def on_tvw_connections_row_activated(self, widget, treepath, column):
        """Edit the selected row on activation"""
        self.ui.action_edit.activate()

    def on_action_delete_activate(self, widget):
        """Remove the selected host"""
        selection = self.ui.tvw_connections.get_selection().get_selected()
        selected_row = selection[1]
        if selected_row and show_message_dialog(
                class_=UIMessageDialogNoYes,
                parent=self.ui.win_main,
                message_type=Gtk.MessageType.QUESTION,
                title=None,
                msg1=_("Remove host"),
                msg2=_("Remove the selected host?"),
                is_response_id=Gtk.ResponseType.YES):
            # Remove the configuration file
            filename = os.path.join(
                DIR_HOSTS, '%s.conf' % self.model.get_key(selected_row))
            if os.path.isfile(filename):
                os.unlink(filename)
            self.model.remove(selected_row)
