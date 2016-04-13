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

from gi.repository import Gtk

import gcentralaccess.settings as settings
from gcentralaccess.gtkbuilder_loader import GtkBuilderLoader
from gcentralaccess.functions import (
    get_ui_file, text, get_list_from_string_list, get_string_fields)

import gcentralaccess.models.services as model_services
from gcentralaccess.models.services import ModelServices

SECTION_WINDOW_NAME = 'association'


class UIServiceAssociation(object):
    def __init__(self, parent, destinations):
        """Prepare the service association dialog"""
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('service_association.glade'))
        self.ui.dialog_association.set_transient_for(parent)
        # Restore the saved size and position
        settings.positions.restore_window_position(
            self.ui.dialog_association, SECTION_WINDOW_NAME)
        # Initialize actions
        for widget in self.ui.get_objects_by_type(Gtk.Action):
            # Connect the actions accelerators
            widget.connect_accelerator()
            # Set labels
            widget.set_label(text(widget.get_label()))
        # Initialize labels
        for widget in self.ui.get_objects_by_type(Gtk.Label):
            widget.set_label(text(widget.get_label()))
            widget.set_tooltip_text(widget.get_label().replace('_', ''))
        # Initialize tooltips
        for widget in self.ui.get_objects_by_type(Gtk.Button):
            action = widget.get_related_action()
            if action:
                widget.set_tooltip_text(action.get_label().replace('_', ''))
        # Load destinations
        self.destinations = destinations
        self.ui.cbo_destinations.set_model(self.destinations.model)
        # Load services
        self.services = ModelServices(self.ui.store_services)
        self.services.load(model_services.services)
        # Connect signals from the glade file to the module functions
        self.ui.connect_signals(self)
        self.service_arguments_widgets = {}

    def show(self, default_destination, default_service):
        """Show the Service association dialog"""
        # Set default destination
        if default_destination:
            self.ui.cbo_destinations.set_active_id(default_destination)
            self.ui.cbo_destinations.set_sensitive(False)
        elif self.destinations.count() > 0:
            self.ui.cbo_destinations.set_active(0)
        # Set default service
        if default_service:
            self.ui.cbo_services.set_active_id(default_service)
        elif self.services.count() > 0:
            self.ui.cbo_services.set_active(0)
        # Show the dialog
        response = self.ui.dialog_association.run()
        self.ui.dialog_association.hide()
        self.destination = self.ui.cbo_destinations.get_active_id()
        self.service = self.ui.cbo_services.get_active_id()
        self.description = self.ui.entry_description.get_text()
        # Prepares argument values
        self.arguments = {}
        for argument in self.service_arguments_widgets:
            (new_label, new_entry) = self.service_arguments_widgets[argument]
            self.arguments[argument] = new_entry.get_text()
        return response

    def destroy(self):
        """Destroy the Service association dialog"""
        settings.positions.save_window_position(
            self.ui.dialog_association, SECTION_WINDOW_NAME)
        self.ui.dialog_association.destroy()
        self.ui.dialog_association = None

    def on_cbo_services_changed(self, widget):
        """Update the service arguments widgets"""
        treeiter = self.ui.cbo_services.get_active_iter()
        # Remove the previously added arguments widgets
        for argument in self.service_arguments_widgets:
            (new_label, new_entry) = self.service_arguments_widgets[argument]
            new_label.destroy()
            new_entry.destroy()
        self.service_arguments_widgets = {}
        # Collect the needed arguments
        command = get_list_from_string_list(
            self.services.get_command(treeiter))
        row_number = 0
        processed_arguments = []
        # The argument address, already has a default widget
        processed_arguments.append('address')
        for option in command:
            arguments = get_string_fields(option)
            # Add a pair of widgets for each argument
            for argument in arguments:
                # Skip existing arguments
                if argument in processed_arguments:
                    continue
                row_number += 1
                processed_arguments.append(argument)
                # Add a new descriptive label for the argument
                new_label = Gtk.Label('%s:' % argument.title())
                new_label.set_xalign(1.0)
                new_label.set_visible(True)
                self.ui.grid_service_arguments.attach(child=new_label,
                                                      left=0,
                                                      top=row_number,
                                                      width=1,
                                                      height=1)
                # Add a new entry for the argument value
                new_entry = Gtk.Entry()
                new_entry.set_visible(True)
                new_entry.set_hexpand(True)
                self.ui.grid_service_arguments.attach(child=new_entry,
                                                      left=1,
                                                      top=row_number,
                                                      width=1,
                                                      height=1)
                # Save a tuple of widgets, to remove later
                self.service_arguments_widgets[argument] = (
                    new_label, new_entry)

    def on_cbo_destinations_changed(self, widget):
        """Update the address entry for the selected destination"""
        treeiter = self.ui.cbo_destinations.get_active_iter()
        self.ui.entry_service_arguments_address.set_text(
            self.destinations.get_value(treeiter))
