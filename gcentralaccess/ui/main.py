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
import json

from gi.repository import Gtk
from gi.repository import Gdk

from gcentralaccess.constants import (
    APP_NAME,
    FILE_SETTINGS, FILE_WINDOWS_POSITION, FILE_SERVICES, DIR_HOSTS)
from gcentralaccess.functions import (
    get_ui_file, get_treeview_selected_row, show_popup_menu, text, _)
import gcentralaccess.preferences as preferences
import gcentralaccess.settings as settings
from gcentralaccess.gtkbuilder_loader import GtkBuilderLoader

import gcentralaccess.models.services as model_services
from gcentralaccess.models.service_info import ServiceInfo
from gcentralaccess.models.host_info import HostInfo
from gcentralaccess.models.hosts import ModelHosts
from gcentralaccess.models.group_info import GroupInfo
from gcentralaccess.models.groups import ModelGroups
from gcentralaccess.models.destination_info import DestinationInfo

import gcentralaccess.ui.debug as debug
import gcentralaccess.ui.processes as processes
from gcentralaccess.ui.about import UIAbout
from gcentralaccess.ui.services import UIServices
from gcentralaccess.ui.groups import UIGroups
from gcentralaccess.ui.host import UIHost
from gcentralaccess.ui.message_dialog import (
    show_message_dialog, UIMessageDialogNoYes, UIMessageDialogClose)

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
        settings.settings = settings.Settings(FILE_SETTINGS, False)
        settings.positions = settings.Settings(FILE_WINDOWS_POSITION, False)
        settings.services = settings.Settings(FILE_SERVICES, False)
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
        self.model_hosts = ModelHosts(self.ui.store_hosts)
        self.model_groups = ModelGroups(self.ui.store_groups)
        # Prepare the debug dialog
        debug.debug = debug.UIDebug(self.ui.win_main,
                                    self.on_window_debug_delete_event)
        # Prepare the processes dialog
        processes.processes = processes.UIProcesses(
            self.ui.win_main, self.on_window_processes_delete_event)
        # Load the groups and hosts list
        self.hosts = {}
        self.reload_groups()
        # Sort the data in the models
        self.model_groups.model.set_sort_column_id(
            self.ui.column_group.get_sort_column_id(),
            Gtk.SortType.ASCENDING)
        self.model_hosts.model.set_sort_column_id(
            self.ui.column_name.get_sort_column_id(),
            Gtk.SortType.ASCENDING)
        # Automatically select the first host if any
        self.ui.tvw_groups.set_cursor(0)
        if self.model_hosts.count() > 0:
            self.ui.tvw_connections.set_cursor(0)
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
        # Set list items row height
        icon_size = preferences.ICON_SIZE
        self.ui.cell_name.props.height = preferences.get(icon_size)
        self.ui.cell_group_name.props.height = preferences.get(icon_size)
        # Set groups visibility
        self.ui.scroll_groups.set_visible(
            preferences.get(preferences.GROUPS_SHOW))
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)

    def run(self):
        """Show the UI"""
        self.ui.win_main.show_all()

    def on_win_main_delete_event(self, widget, event):
        """Save the settings and close the application"""
        debug.debug.destroy()
        processes.processes.destroy()
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
        selected_row = get_treeview_selected_row(self.ui.tvw_connections)
        if selected_row:
            iter_parent = self.ui.store_hosts.iter_parent(selected_row)
            selected_path = self.model_hosts.model[selected_row].path
            # Get the path of the host
            if iter_parent is None:
                tree_path = self.model_hosts.model[selected_row].path
            else:
                tree_path = self.model_hosts.model[iter_parent].path
            expanded = self.ui.tvw_connections.row_expanded(tree_path)
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
        if selected_row:
            # Automatically expand the row if it was expanded before
            if expanded:
                self.ui.tvw_connections.expand_row(tree_path, True)
            # Automatically select again the previously selected row
            self.ui.tvw_connections.set_cursor(path=selected_path,
                                               column=None,
                                               start_editing=False)

    def reload_hosts(self):
        """Load hosts from the settings files"""
        self.model_hosts.clear()
        self.hosts.clear()
        hosts_path = self.get_current_group_path()
        # Fix bug where the groups model isn't yet emptied, resulting in
        # being still used after a clear, then an invalid path
        if not os.path.isdir(hosts_path):
            return
        for filename in os.listdir(hosts_path):
            # Skip folders, used for groups
            if os.path.isdir(os.path.join(hosts_path, filename)):
                continue
            settings_host = settings.Settings(
                filename=os.path.join(hosts_path, filename),
                case_sensitive=True)
            name = settings_host.get(SECTION_HOST, SECTION_HOST_NAME)
            description = settings_host.get(SECTION_HOST,
                                            SECTION_HOST_DESCRIPTION)
            host = HostInfo(name=name, description=description)
            destinations = {}
            # Load host destinations
            if SECTION_DESTINATIONS in settings_host.get_sections():
                for option in settings_host.get_options(SECTION_DESTINATIONS):
                    value = settings_host.get(SECTION_DESTINATIONS, option)
                    destinations[option] = DestinationInfo(name=option,
                                                           value=value)
                    # Load associations
                    associations = settings_host.get_list(SECTION_ASSOCIATIONS,
                                                          option,
                                                          ';')
                    for association in associations:
                        if ':' in association:
                            service, arguments = association.split(':', 1)
                        else:
                            # No association arguments, set empty arguments
                            service = association
                            arguments = '{}'
                        destinations[option].associations.append(
                            (service, json.loads(arguments)))
            self.add_host(host, destinations, False)

    def add_host(self, host, destinations, update_settings):
        """Add a new host along as with its destinations"""
        # Add the host to the data and to the model
        self.hosts[host.name] = host
        treeiter = self.model_hosts.add_data(host)
        # Add the destinations to the data
        for destination_name in destinations:
            destination = destinations[destination_name]
            host.add_destination(item=destination)
            # Add service associations to the model
            for service_name, service_arguments in destination.associations:
                if service_name in model_services.services:
                    service = model_services.services[service_name]
                    arguments = json.dumps(service_arguments)
                    self.model_hosts.add_association(treeiter=treeiter,
                                                     destination=destination,
                                                     service=service,
                                                     arguments=arguments)
                else:
                    debug.add_warning('service %s not found' % service_name)
        # Update settings file if requested
        if update_settings:
            hosts_path = self.get_current_group_path()
            settings_host = settings.Settings(
                filename=os.path.join(hosts_path, '%s.conf' % host.name),
                case_sensitive=True)
            # Add host information
            settings_host.set(SECTION_HOST, SECTION_HOST_NAME, host.name)
            settings_host.set(SECTION_HOST, SECTION_HOST_DESCRIPTION,
                              host.description)
            # Add destinations
            for key in host.destinations:
                destination = host.destinations[key]
                settings_host.set(SECTION_DESTINATIONS,
                                  destination.name,
                                  destination.value)
                # Add associations to the settings
                settings_host.set(section=SECTION_ASSOCIATIONS,
                                  option=destination.name,
                                  value=';'.join(
                                    ['%s:%s' % (service_name,
                                                json.dumps(service_arguments))
                                        for service_name, service_arguments
                                        in destination.associations]))
            # Save the settings to the file
            settings_host.save()

    def remove_host(self, name):
        """Remove a host by its name"""
        hosts_path = self.get_current_group_path()
        filename = os.path.join(hosts_path, '%s.conf' % name)
        if os.path.isfile(filename):
            os.unlink(filename)
        self.hosts.pop(name)
        self.model_hosts.remove(self.model_hosts.get_iter(name))

    def reload_groups(self):
        """Load groups from hosts folder"""
        self.model_groups.clear()
        # Always add a default group
        self.model_groups.add_data(GroupInfo('', _('Default group')))
        for filename in os.listdir(DIR_HOSTS):
            if os.path.isdir(os.path.join(DIR_HOSTS, filename)):
                # For each folder add a new group
                self.model_groups.add_data(GroupInfo(filename, filename))

    def on_action_new_activate(self, action):
        """Define a new host"""
        dialog = UIHost(parent=self.ui.win_main, hosts=self.model_hosts)
        response = dialog.show(default_name='',
                               default_description='',
                               title=_('Add a new host'),
                               treeiter=None)
        if response == Gtk.ResponseType.OK:
            destinations = dialog.destinations.dump()
            associations = dialog.associations.dump()
            for values in associations:
                (destination_name, service_name, service_arguments) = \
                    associations[values]
                destination = destinations[destination_name]
                destination.associations.append(
                    (service_name, service_arguments))
            self.add_host(HostInfo(name=dialog.name,
                                   description=dialog.description),
                          destinations=destinations,
                          update_settings=True)
            # Automatically select the newly added host
            self.ui.tvw_connections.set_cursor(
                path=self.model_hosts.get_path_by_name(dialog.name),
                column=None,
                start_editing=False)
        dialog.destroy()

    def on_action_edit_activate(self, action):
        """Define a new host"""
        selected_row = get_treeview_selected_row(self.ui.tvw_connections)
        if selected_row:
            if self.is_selected_row_host():
                # First level (host)
                name = self.model_hosts.get_key(selected_row)
                description = self.model_hosts.get_description(selected_row)
                selected_iter = self.model_hosts.get_iter(name)
                expanded = self.ui.tvw_connections.row_expanded(
                    self.model_hosts.get_path(selected_iter))
                dialog = UIHost(parent=self.ui.win_main,
                                hosts=self.model_hosts)
                # Restore the destinations for the selected host
                destinations = self.hosts[name].destinations
                for destination_name in destinations:
                    destination = destinations[destination_name]
                    dialog.destinations.add_data(destination)
                    for (service_name, arguments) in destination.associations:
                        if service_name in model_services.services:
                            dialog.associations.add_data(
                                index=dialog.associations.count(),
                                name=destination_name,
                                service=model_services.services[service_name],
                                arguments=arguments)
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
                        (destination_name, service_name, service_arguments) = \
                            associations[values]
                        destination = destinations[destination_name]
                        destination.associations.append(
                            (service_name, service_arguments))
                    self.remove_host(name)
                    self.add_host(HostInfo(name=dialog.name,
                                           description=dialog.description),
                                  destinations=destinations,
                                  update_settings=True)
                    # Get the path of the host
                    tree_path = self.model_hosts.get_path_by_name(dialog.name)
                    # Automatically select again the previously selected host
                    self.ui.tvw_connections.set_cursor(path=tree_path,
                                                       column=None,
                                                       start_editing=False)
                    # Automatically expand the row if it was expanded before
                    if expanded:
                        self.ui.tvw_connections.expand_row(tree_path, False)

    def on_tvw_connections_row_activated(self, widget, treepath, column):
        """Edit the selected row on activation"""
        selected_row = get_treeview_selected_row(self.ui.tvw_connections)
        if selected_row and self.is_selected_row_host():
            # Start host edit
            self.ui.action_edit.activate()
        else:
            # Connect to the destination
            self.ui.action_connect.activate()

    def on_action_delete_activate(self, action):
        """Remove the selected host"""
        selected_row = get_treeview_selected_row(self.ui.tvw_connections)
        if selected_row and show_message_dialog(
                class_=UIMessageDialogNoYes,
                parent=self.ui.win_main,
                message_type=Gtk.MessageType.QUESTION,
                title=None,
                msg1=_("Remove host"),
                msg2=_("Remove the selected host?"),
                is_response_id=Gtk.ResponseType.YES):
            self.remove_host(self.model_hosts.get_key(selected_row))

    def on_tvw_connections_cursor_changed(self, widget):
        """Set actions sensitiveness for host and connection"""
        if get_treeview_selected_row(self.ui.tvw_connections):
            self.ui.actions_connection.set_sensitive(
                not self.is_selected_row_host())
            self.ui.actions_host.set_sensitive(self.is_selected_row_host())

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

    def on_action_processes_toggled(self, action):
        """Show and hide the processes window"""
        if self.ui.action_processes.get_active():
            processes.processes.show()
        else:
            processes.processes.hide()

    def on_window_processes_delete_event(self, widget, event):
        """Catch the delete_event in the processes window to hide the window"""
        self.ui.action_processes.set_active(False)
        return True

    def on_tvw_connections_key_press_event(self, widget, event):
        """Expand and collapse nodes with keyboard arrows"""
        if event.keyval in (Gdk.KEY_Left, Gdk.KEY_Right):
            # Collapse or expand the selected row using <Left> and <Right>
            selected_row = get_treeview_selected_row(self.ui.tvw_connections)
            if (selected_row and self.is_selected_row_host()):
                tree_path = self.model_hosts.get_path(selected_row)
                expanded = self.ui.tvw_connections.row_expanded(tree_path)
                if event.keyval == Gdk.KEY_Left and expanded:
                    # Collapse the selected node
                    self.ui.tvw_connections.collapse_row(tree_path)
                elif event.keyval == Gdk.KEY_Right and not expanded:
                    # Expand the selected node
                    self.ui.tvw_connections.expand_row(tree_path, False)
                return True
        elif event.keyval in (Gdk.KEY_Page_Up, Gdk.KEY_Page_Down) and \
                event.state & Gdk.ModifierType.CONTROL_MASK:
            # Change group using <Control>+<Page Up> and <Control>+<Page Down>
            selected_row = get_treeview_selected_row(self.ui.tvw_groups)
            if event.keyval == Gdk.KEY_Page_Down:
                # Next group
                new_iter = self.model_groups.model.iter_next(selected_row)
            elif event.keyval == Gdk.KEY_Page_Up:
                # Previous row
                new_iter = self.model_groups.model.iter_previous(selected_row)
            if new_iter:
                # Select the newly selected row in the groups list
                new_path = self.model_groups.get_path(new_iter)
                self.ui.tvw_groups.set_cursor(new_path)
                # Automatically select the first host for the group
                self.ui.tvw_connections.set_cursor(0)
            return True

    def on_action_connect_activate(self, action):
        """Establish the connection for the destination"""
        selected_row = get_treeview_selected_row(self.ui.tvw_connections)
        if selected_row and not self.is_selected_row_host():
            host = self.hosts[self.model_hosts.get_key(
                self.ui.store_hosts.iter_parent(selected_row))]
            destination_name = self.model_hosts.get_key(selected_row)
            destination = host.destinations[destination_name]
            associations = [service_name for service_name, arguments
                            in destination.associations]
            service_name = self.model_hosts.get_service(selected_row)
            service_arguments = self.model_hosts.get_arguments(selected_row)
            if service_name in associations:
                service = model_services.services[service_name]
                command = service.command
                # Prepares the arguments
                arguments_map = {}
                arguments_map['address'] = destination.value
                for key in service_arguments:
                    arguments_map[key] = service_arguments[key]
                # Execute command
                try:
                    command = command.format(**arguments_map)
                    processes.processes.add_process(host,
                                                    destination,
                                                    service,
                                                    command)
                except KeyError as error:
                    # An error occurred processing the command
                    error_msg1 = _('Connection open failed')
                    error_msg2 = _('An error occurred processing the '
                                   'service command.')
                    show_message_dialog(
                        class_=UIMessageDialogClose,
                        parent=self.ui.win_main,
                        message_type=Gtk.MessageType.ERROR,
                        title=None,
                        msg1=error_msg1,
                        msg2=error_msg2,
                        is_response_id=None)
                    debug.add_error(error_msg2)
                    debug.add_error('Host: "%s"' % host.name)
                    debug.add_error('Destination name: "%s"' %
                                    destination.name)
                    debug.add_error('Destination value: "%s"' %
                                    destination.value)
                    debug.add_error('Service: %s' % service.name),
                    debug.add_error('Command: "%s"' % command)
            else:
                debug.add_warning('service %s not found' % service_name)

    def is_selected_row_host(self):
        """Return if the currently selected row is an host"""
        return self.ui.store_hosts.iter_parent(
            get_treeview_selected_row(self.ui.tvw_connections)) is None

    def get_current_group_path(self):
        """Return the path of the currently selected group"""
        selected_row = get_treeview_selected_row(self.ui.tvw_groups)
        group_name = self.model_groups.get_key(selected_row) if selected_row \
            else ''
        return os.path.join(DIR_HOSTS, group_name) if group_name else DIR_HOSTS

    def on_tvw_groups_cursor_changed(self, widget):
        """Set actions sensitiveness for host and connection"""
        if get_treeview_selected_row(self.ui.tvw_groups):
            self.reload_hosts()

    def on_action_groups_activate(self, widget):
        """Edit groups"""
        dialog_groups = UIGroups(parent=self.ui.win_main)
        dialog_groups.model = self.model_groups
        dialog_groups.ui.tvw_groups.set_model(self.model_groups.model)
        dialog_groups.show()
        dialog_groups.destroy()

    def on_tvw_groups_button_release_event(self, widget, event):
        """Show groups popup menu on right click"""
        if event.button == Gdk.BUTTON_SECONDARY:
            show_popup_menu(self.ui.menu_groups, event.button)

    def on_tvw_connections_button_release_event(self, widget, event):
        """Show connections popup menu on right click"""
        if event.button == Gdk.BUTTON_SECONDARY:
            show_popup_menu(self.ui.menu_connections, event.button)
