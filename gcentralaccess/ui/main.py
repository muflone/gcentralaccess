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

import os
import os.path

from gi.repository import Gtk
from gi.repository import Gdk

from gcentralaccess.constants import (
    APP_NAME,
    FILE_SETTINGS, FILE_WINDOWS_POSITION, FILE_SERVICES, DIR_HOSTS)
from gcentralaccess.functions import get_ui_file, text, _
import gcentralaccess.preferences as preferences
import gcentralaccess.settings as settings
from gcentralaccess.gtkbuilder_loader import GtkBuilderLoader

import gcentralaccess.models.services as model_services
from gcentralaccess.models.service_info import ServiceInfo
from gcentralaccess.models.host_info import HostInfo
from gcentralaccess.models.hosts import ModelHosts
from gcentralaccess.models.destination_info import DestinationInfo
import gcentralaccess.models.destination_types as destination_types
from gcentralaccess.models.destination_types import ModelDestinationTypes

import gcentralaccess.ui.debug as debug
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
SECTION_ASSOCIATIONS = 'associations'


class UIMain(object):
    def __init__(self, application):
        self.application = application
        # Load settings
        settings.settings = settings.Settings(FILE_SETTINGS)
        settings.positions = settings.Settings(FILE_WINDOWS_POSITION)
        settings.services = settings.Settings(FILE_SERVICES)
        preferences.preferences = preferences.Preferences()
        # Load services
        for key in settings.services.get_sections():
            model_services.services[key] = ServiceInfo(
                name=key,
                description=settings.services.get(
                    key, SECTION_SERVICE_DESCRIPTION),
                command=settings.services.get(
                    key, SECTION_SERVICE_COMMAND),
                terminal=settings.services.get_boolean(
                    key, SECTION_SERVICE_TERMINAL),
                icon=settings.services.get(
                    key, SECTION_SERVICE_ICON))
        self.loadUI()
        self.model = ModelHosts(self.ui.store_hosts)
        # Prepare the debug dialog
        debug.debug = debug.UIDebug(self.ui.win_main,
                                    self.on_window_debug_delete_event)
        # This model is shared across the main and the destination detail
        destination_types.destination_types = ModelDestinationTypes(
            self.ui.store_destination_types)
        self.hosts = {}
        self.reload_hosts()
        # Sort the data in the models
        self.model.model.set_sort_column_id(
            self.ui.column_name.get_sort_column_id(),
            Gtk.SortType.ASCENDING)
        # Restore the saved size and position
        settings.positions.restore_window_position(
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
            # Set labels
            widget.set_label(text(widget.get_label()))
        # Initialize tooltips
        for widget in self.ui.get_objects_by_type(Gtk.ToolButton):
            action = widget.get_related_action()
            if action:
                widget.set_tooltip_text(action.get_label().replace('_', ''))
        # Initialize column headers
        for widget in self.ui.get_objects_by_type(Gtk.TreeViewColumn):
            widget.set_title(text(widget.get_title()))
        self.ui.cell_name.props.height = preferences.get(preferences.ICON_SIZE)
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def run(self):
        """Show the UI"""
        self.ui.win_main.show_all()

    def on_win_main_delete_event(self, widget, event):
        """Save the settings and close the application"""
        debug.debug.destroy()
        settings.positions.save_window_position(
            self.ui.win_main, SECTION_WINDOW_NAME)
        settings.positions.save()
        settings.services.save()
        settings.settings.save()
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
        dialog_services = UIServices(parent=self.ui.win_main)
        # Load services list
        dialog_services.model.load(model_services.services)
        dialog_services.show()
        # Get the new services list, clear and store the list again
        model_services.services = dialog_services.model.dump()
        dialog_services.destroy()
        settings.services.clear()
        for key in model_services.services.iterkeys():
            settings.services.set(
                section=key,
                option=SECTION_SERVICE_DESCRIPTION,
                value=model_services.services[key].description)
            settings.services.set(
                section=key,
                option=SECTION_SERVICE_COMMAND,
                value=model_services.services[key].command)
            settings.services.set_boolean(
                section=key,
                option=SECTION_SERVICE_TERMINAL,
                value=model_services.services[key].terminal)
            settings.services.set(
                section=key,
                option=SECTION_SERVICE_ICON,
                value=model_services.services[key].icon)
        self.reload_hosts()

    def reload_hosts(self):
        """Load hosts from the settings files"""
        self.model.clear()
        self.hosts.clear()
        for filename in os.listdir(DIR_HOSTS):
            settings_host = settings.Settings(
                os.path.join(DIR_HOSTS, filename))
            name = settings_host.get(SECTION_HOST, SECTION_HOST_NAME)
            description = settings_host.get(SECTION_HOST,
                                            SECTION_HOST_DESCRIPTION)
            host = HostInfo(name=name, description=description)
            destinations = {}
            # Load host destinations
            if SECTION_DESTINATIONS in settings_host.get_sections():
                for option in settings_host.get_options(SECTION_DESTINATIONS):
                    values = settings_host.get(SECTION_DESTINATIONS, option)
                    type, value = values.split(':', 1)
                    treeiter = destination_types.get_iter(type)
                    destinations[option] = DestinationInfo(
                        name=option,
                        value=value,
                        type=type,
                        type_local=destination_types.get_description(treeiter))
                    # Load associations
                    values = settings_host.get_list(SECTION_ASSOCIATIONS,
                                                    option)
                    if values:
                        destinations[option].associations.extend(values)
            self.add_host(host, destinations, False)

    def add_host(self, host, destinations, update_settings):
        """Add a new host along as with its destinations"""
        # Add the host to the data and to the model
        self.hosts[host.name] = host
        treeiter = self.model.add_data(host)
        # Add the destinations to the data
        for destination_name in destinations:
            destination = destinations[destination_name]
            host.add_destination(item=destination)
            # Add service associations to the model
            for service_name in destination.associations:
                if service_name in model_services.services:
                    service = model_services.services[service_name]
                    self.model.add_association(treeiter=treeiter,
                                               destination=destination,
                                               service=service)
                else:
                    debug.add_warning('service %s not found' % service_name)
        # Update settings file if requested
        if update_settings:
            settings_host = settings.Settings(
                os.path.join(DIR_HOSTS, '%s.conf' % host.name))
            # Add host information
            settings_host.set(SECTION_HOST, SECTION_HOST_NAME, host.name)
            settings_host.set(SECTION_HOST, SECTION_HOST_DESCRIPTION,
                              host.description)
            # Add destinations
            for key in host.destinations:
                destination = host.destinations[key]
                settings_host.set(SECTION_DESTINATIONS,
                                  destination.name,
                                  '%s:%s' % (destination.type,
                                             destination.value))
                # Add associations to the settings
                settings_host.set(section=SECTION_ASSOCIATIONS,
                                  option=destination.name,
                                  value=','.join(destination.associations))
            # Save the settings to the file
            settings_host.save()

    def remove_host(self, name):
        """Remove a host by its name"""
        filename = os.path.join(DIR_HOSTS, '%s.conf' % name)
        if os.path.isfile(filename):
            os.unlink(filename)
        self.hosts.pop(name)
        self.model.remove(self.model.get_iter(name))

    def on_action_new_activate(self, action):
        """Define a new host"""
        dialog = UIHost(parent=self.ui.win_main, hosts=self.model)
        response = dialog.show(default_name='',
                               default_description='',
                               title=_('Add a new host'),
                               treeiter=None)
        if response == Gtk.ResponseType.OK:
            destinations = dialog.destinations.dump()
            associations = dialog.associations.dump()
            for values in associations:
                destination_name, service_name = associations[values]
                destination = destinations[destination_name]
                destination.associations.append(service_name)
            self.add_host(HostInfo(name=dialog.name,
                                   description=dialog.description),
                          destinations=destinations,
                          update_settings=True)
            # Automatically select the newly added host
            self.ui.tvw_connections.set_cursor(
                path=self.model.get_path_by_name(dialog.name),
                column=None,
                start_editing=False)
        dialog.destroy()

    def on_action_edit_activate(self, action):
        """Define a new host"""
        selection = self.ui.tvw_connections.get_selection().get_selected()
        selected_row = selection[1]
        if selected_row:
            if self.ui.store_hosts.iter_parent(selected_row) is None:
                # First level (host)
                name = self.model.get_key(selected_row)
                description = self.model.get_description(selected_row)
                selected_iter = self.model.get_iter(name)
                expanded = self.ui.tvw_connections.row_expanded(
                    self.model.get_path(selected_iter))
                dialog = UIHost(parent=self.ui.win_main, hosts=self.model)
                # Restore the destinations for the selected host
                destinations = self.hosts[name].destinations
                for destination_name in destinations:
                    destination = destinations[destination_name]
                    dialog.destinations.add_data(destination)
                    for service_name in destination.associations:
                        if service_name in model_services.services:
                            dialog.associations.add_data(
                                index=dialog.associations.count(),
                                name=destination_name,
                                service=model_services.services[service_name])
                        else:
                            debug.add_warning('service %s not found' %
                                              service_name)
                # Show the edit host dialog
                response = dialog.show(default_name=name,
                                       default_description=description,
                                       title=_('Edit host'),
                                       treeiter=selected_iter)
                if response == Gtk.ResponseType.OK:
                    # Remove older host and add the newer
                    destinations = dialog.destinations.dump()
                    associations = dialog.associations.dump()
                    for values in associations:
                        destination_name, service_name = associations[values]
                        destination = destinations[destination_name]
                        destination.associations.append(service_name)
                    self.remove_host(name)
                    self.add_host(HostInfo(name=dialog.name,
                                           description=dialog.description),
                                  destinations=destinations,
                                  update_settings=True)
                    # Get the path of the host
                    tree_path = self.model.get_path_by_name(dialog.name)
                    # Automatically select again the previously selected host
                    self.ui.tvw_connections.set_cursor(path=tree_path,
                                                       column=None,
                                                       start_editing=False)
                    # Automatically expand the row if it was expanded before
                    if expanded:
                        self.ui.tvw_connections.expand_row(tree_path, False)

    def on_tvw_connections_row_activated(self, widget, treepath, column):
        """Edit the selected row on activation"""
        self.ui.action_edit.activate()

    def on_action_delete_activate(self, action):
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
            self.remove_host(self.model.get_key(selected_row))

    def on_action_debug_toggled(self, action):
        """Show and hide the debug window"""
        if self.ui.action_debug.get_active():
            debug.debug.show()
        else:
            debug.debug.hide()

    def on_window_debug_delete_event(self, widget, event):
        """Catch the delete_event in the debug window to hide the window"""
        self.ui.action_debug.set_active(False)
        return True
